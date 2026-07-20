from dataclasses import dataclass

@dataclass
class Game:
    date: str
    venue: str
    level: str
    start_time: str
    end_time: str
    price: str | None = None
    original_message: str = ""