from bs4 import BeautifulSoup
import re
from typing import List

from model.conversation import ConversationChunk, Conversation

NEWLINE_PATTERN = r"\n"


class TranscriptParser():
    def __init__(self):
        pass
    
    def parse_html(self, html: str) -> List[ConversationChunk]:
        soup = BeautifulSoup(html, "html.parser")

        conversation_chunks = soup.find_all("div", class_="ts-segment")
        speaker = ""
        conversation = []

        for chunk in conversation_chunks:
            cur_speaker = chunk.find(class_="ts-name").get_text()
            ts = chunk.find(class_="ts-timestamp").contents[0].get_text()[1:-1]
            ts_sortable = 3600 * int(ts[0]+ts[1]) + 60 * int(ts[3]+ts[4]) + int(ts[6]+ts[7])
            text = chunk.find(class_="ts-text").get_text()
            text = re.sub(NEWLINE_PATTERN, "", text)
            speaker = cur_speaker or speaker
            parsed_chunk = ConversationChunk(speaker, timestamp=ts, ts_sortable=ts_sortable, text=text)
            conversation.append(parsed_chunk)
        
        return conversation

    def parse_html_file(self, file_name: str):
        with open(file_name) as f:
            return self.parse_html(f.read())

