import re

from num2words import num2words

from model.conversation import Conversation, ConversationChunk


ORDINALS_PATTERN = r"(\d+)(st|nd|rd|th)"
CARDINALS_PATTERN = r"\d+"

class Preprocessor():
    def __init__(self):
        pass

    def replace_numbers(self, conv: Conversation) -> Conversation:
        transformed = self._ordinals_to_words(conv)
        return self._cardinals_to_words(transformed)

    def _cardinals_to_words(self, conv: Conversation) -> Conversation:
        transformed = []
        for chunk in conv.conversation:
            matches = re.findall(CARDINALS_PATTERN, chunk.text)
            for match in matches:
                chunk.text=chunk.text.replace(match, num2words(match))

            transformed.append(ConversationChunk(
                chunk.speaker,
                chunk.timestamp,
                chunk.ts_sortable,
                chunk.text
            ))
        
        return Conversation(transformed)

    def _ordinals_to_words(self, conv: Conversation) -> Conversation:
        transformed = []
        for chunk in conv.conversation:
            matches = re.findall(ORDINALS_PATTERN, chunk.text)
            for match in matches:
                chunk.text = chunk.text.replace(match[0]+match[1], num2words(match[0], ordinal=True))
            
            transformed.append(ConversationChunk(
                chunk.speaker,
                chunk.timestamp,
                chunk.ts_sortable,
                chunk.text
            ))
        
        return Conversation(transformed)


