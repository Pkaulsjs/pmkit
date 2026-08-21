"""Typed configuration with safe defaults."""
import json
import os
from dataclasses import dataclass, fields


@dataclass
class Config:
    scan_threshold: float = 0.995
    negrisk_buffer: float = 0.02
    max_pages: int = 10
    paper_starting_cash: float = 1000.0

    @classmethod
    def from_json(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        known = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in raw.items() if k in known}
        return cls(**filtered)


def load_config(path=None):
    if path and os.path.exists(path):
        return Config.from_json(path)
    return Config()
