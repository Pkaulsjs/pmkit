import os, sys, struct, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pmkit import stream as st


class TestFrameCodec(unittest.TestCase):
    def _roundtrip(self, text):
        """Encode with send_text logic, decode with recv_text logic over a socketpair."""
        import socket
        a, b = socket.socketpair()
        ws = st.WSClient.__new__(st.WSClient)
        ws.sock = a
        ws._buf = b""
        ws.closed = False
        ws.send_text(text)
        # read raw frame from the other end, strip mask, compare payload
        hdr = b.recv(2)
        b1, b2 = hdr[0], hdr[1]
        ln = b2 & 0x7F
        if ln == 126:
            ln = struct.unpack(">H", b.recv(2))[0]
        elif ln == 127:
            ln = struct.unpack(">Q", b.recv(8))[0]
        mask = b.recv(4)
        payload = b""
        while len(payload) < ln:
            chunk = b.recv(ln - len(payload))
            if not chunk:
                break
            payload += chunk
        unmasked = bytes(x ^ mask[i % 4] for i, x in enumerate(payload))
        self.assertEqual(unmasked.decode(), text)
        self.assertEqual(b1 & 0x0F, 0x1)  # text opcode

    def test_small(self):
        self._roundtrip("hello")

    def test_medium(self):
        self._roundtrip("x" * 500)

    def test_large(self):
        self._roundtrip("y" * 70000)


if __name__ == "__main__":
    unittest.main()
