from dataclasses import dataclass


@dataclass
class Target:
    id: str
    host: str
    port: str = 502
