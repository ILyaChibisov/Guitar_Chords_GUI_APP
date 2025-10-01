from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Song:
    """Модель данных песни"""
    id: int
    title: str
    artist: str
    chords: List[str]
    file_path: str
    content: str

@dataclass
class Chord:
    """Модель данных аккорда"""
    id: int
    name: str
    folder: str

@dataclass
class ChordVariant:
    """Модель данных варианта аккорда"""
    id: int
    chord_id: int
    image_path: str
    sound_path: str
    position: int