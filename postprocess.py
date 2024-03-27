import re

from metaflow import FlowSpec, step, Parameter
from num2words import num2words

from model.conversation import Conversation, ConversationChunk

class PostprocessPipeline(FlowSpec):
    filename = Parameter('filename',
                               help='name of the file to postprocess')
    language_code = Parameter('lang',
                               help='language of conv in the file')

    @step
    def start(self):
        self.transcript_json_path = f"{self.filename}-{self.language_code}.json"
        self.conversation = Conversation()
        self.conversation.from_json(self.transcript_json_path)
        self.next(self.replace_numbers)

    @step
    def replace_numbers(self):
        transformed = []
        for chunk in self.conversation.conversation:
            matches = re.findall(r"\d+", chunk.text)
            for match in matches:
                chunk.text=chunk.text.replace(match, num2words(match, lang="cz"))

            transformed.append(ConversationChunk(
                chunk.speaker,
                chunk.timestamp,
                chunk.ts_sortable,
                chunk.text
            ))
        self.conversation = Conversation(transformed)
        self.next(self.save_to_file)
    
    @step
    def save_to_file(self):
        self.conversation.save_as_json(self.transcript_json_path)
        self.next(self.end)

    @step
    def end(self):
        pass
        
if __name__ == '__main__':
    PostprocessPipeline()
