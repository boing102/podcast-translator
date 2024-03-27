from typing import List, Optional
from dataclasses import dataclass
import json


@dataclass
class ConversationChunk():
    speaker: str
    timestamp: str
    ts_sortable: int # seconds from the beginning
    text: str


class Conversation():
    def __init__(self, conversation: Optional[List[ConversationChunk]] = None) -> None:
        self.conversation = conversation

    def from_json(self, filename: str):
        with open(filename) as fp:
            self.conversation = [ConversationChunk(chunk["speaker"], chunk["timestamp"], chunk["ts_sortable"], chunk["text"]) for chunk in json.load(fp)]

    def save_as_json(self, filename: str) -> None:
        if not self.conversation:
            raise ValueError("Read a conversation first!")
        conv_json = [e.__dict__ for e in self.conversation]
        with open(filename, "w") as fp:
            json.dump(conv_json, fp, ensure_ascii=False)
    
    def get_speaker_chunks(self, speaker: str) -> List[ConversationChunk]:
        return [chunk for chunk in self.conversation if chunk.speaker == speaker]
        
