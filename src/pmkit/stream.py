"""Minimal WebSocket client (stdlib-only) + Polymarket market channel.

Implements just enough of RFC 6455 for read-only streaming: handshake,
text frame decoding, ping/pong. No external dependencies.
"""
import base64
import json
import os
import socket
import ssl
import struct
import time
from urllib.parse import urlparse

MARKET_WSS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"


class WSClient:
    """Tiny blocking WebSocket client for text frames."""

    def __init__(self, host, path, timeout=10.0):
        self.closed = False
        raw = socket.create_connection((host, 443), timeout=timeout)
        self.sock = ssl.create_default_context().wrap_socket(raw, server_hostname=host)
        self.sock.settimeout(1.0)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("closed during handshake")
            resp += chunk
        status = resp.split(b"\r\n")[0]
        if b"101" not in status:
            raise ConnectionError("handshake failed: " + status.decode(errors="replace"))
        self._buf = resp.split(b"\r\n\r\n", 1)[1]

    def recv_text(self):
        """Next text message; None only when peer closes. Raises socket.timeout when idle."""
        while True:
            header = self._recv_exact(2)
            if header is None:
                return None
            b1, b2 = header
            opcode = b1 & 0x0F
            masked = b2 & 0x80
            length = b2 & 0x7F
            if length == 126:
                ext = self._recv_exact(2)
                if ext is None:
                    return None
                length = struct.unpack(">H", ext)[0]
            elif length == 127:
                ext = self._recv_exact(8)
                if ext is None:
                    return None
                length = struct.unpack(">Q", ext)[0]
            mask = self._recv_exact(4) if masked else None
            payload = self._recv_exact(length) if length else b""
            if payload is None and length:
                return None
            if mask:
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            if opcode == 0x1:
                return payload.decode("utf-8", errors="replace")
            if opcode == 0x9:
                self._send_pong(payload)
            if opcode == 0x8:
                self.closed = True
                return None

    def send_text(self, text):
        """Send a masked text frame (client-to-server frames must be masked)."""
        payload = text.encode()
        n = len(payload)
        frame = bytearray([0x81])
        if n < 126:
            frame.append(0x80 | n)
        elif n < 65536:
            frame.append(0x80 | 126)
            frame += struct.pack(">H", n)
        else:
            frame.append(0x80 | 127)
            frame += struct.pack(">Q", n)
        mask = os.urandom(4)
        frame += mask
        frame += bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(frame))

    def _recv_exact(self, n):
        """Raise socket.timeout when idle; return None only on EOF."""
        buf = self._buf
        while len(buf) < n:
            chunk = self.sock.recv(65536)  # may raise socket.timeout
            if not chunk:
                self.closed = True
                return None
            buf += chunk
        self._buf = buf[n:]
        return buf[:n]

    def _send_pong(self, payload):
        n = len(payload)
        frame = bytearray([0x8A])
        if n < 126:
            frame.append(0x80 | n)
        elif n < 65536:
            frame.append(0x80 | 126)
            frame += struct.pack(">H", n)
        else:
            return
        mask = os.urandom(4)
        frame += mask
        frame += bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        try:
            self.sock.sendall(bytes(frame))
        except OSError:
            pass


def stream_market(asset_ids, on_message, duration=30.0):
    """Subscribe to the market channel for asset_ids; call on_message(dict)."""
    u = urlparse(MARKET_WSS)
    ws = WSClient(u.hostname, u.path)
    sub = json.dumps({"assets_ids": list(asset_ids), "type": "market"})
    ws.send_text(sub)
    end = time.time() + duration
    while time.time() < end:
        try:
            msg = ws.recv_text()
        except socket.timeout:
            continue
        if msg is None:
            break
        try:
            data = json.loads(msg)
        except ValueError:
            continue
        on_message(data)
    ws.sock.close()
