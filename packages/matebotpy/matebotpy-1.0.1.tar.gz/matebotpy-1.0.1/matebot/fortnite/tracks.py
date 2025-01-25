from dataclasses import dataclass

@dataclass
class SparkTrack:
    title: str
    releaseYear: float
    duration: float
    album: str
    artist: str
    bpm: float
    scale: str
    albumArt: str
    midiData: str