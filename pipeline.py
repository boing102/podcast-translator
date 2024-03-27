import os

import deepl
from metaflow import FlowSpec, step, Parameter
import requests

from parsers import TranscriptParser
from model.conversation import Conversation, ConversationChunk
from preprocessor import Preprocessor

class Pipeline(FlowSpec):
    transcript_url = Parameter('url',
                               help='Url of the transcript webpage')

    @step
    def start(self):
        print(f"Running for {self.transcript_url}")
        self.filename = self.transcript_url.split("/")[-1]
        self.transcript_html_path = self.filename + ".html"
        self.transcript_json_path = self.filename + ".json"
        self.next(self.download_transcript)

    @step
    def download_transcript(self):
        if not os.path.exists(self.transcript_html_path):
            print(f"Downloading {self.transcript_url} & saving to {self.transcript_html_path}")
            with open(self.transcript_html_path, "wb") as f:
                response = requests.get(self.transcript_html_path)
                f.write(response.content)
        else:
            print(f"Skipping download, file {self.transcript_html_path} exists...")

        self.next(self.parse_transcript)
    
    @step
    def parse_transcript(self):
        p = TranscriptParser()
        parsed_conv = p.parse_html_file(self.transcript_html_path)
        self.conversation = Conversation(conversation=parsed_conv)
        
        self.next(self.replace_numbers)
    
    @step
    def replace_numbers(self):
        pre = Preprocessor()
        self.conversation = pre.replace_numbers(self.conversation)

        self.next(self.save_to_file)
    
    @step
    def save_to_file(self):
        self.conversation.save_as_json(self.transcript_json_path)
        self.conv_chunks = self.conversation.conversation
        self.next(self.parallel_translate, foreach="conv_chunks")

    
    @step
    def parallel_translate(self):
        chunk: ConversationChunk = self.input
        translator = deepl.Translator(os.environ["DEEPL_API_KEY"])

        chunk.text = translator.translate_text(chunk.text, target_lang="CS").text
        self.chunk = chunk
        self.next(self.tranlation_join)
    
    @step
    def tranlation_join(self, chunks):
        self.translated_conv = [chunk.chunk for chunk in chunks]
        self.translated_conv = sorted(self.translated_conv, key=lambda chunk: chunk.ts_sortable)
        self.chunk = None
        self.conv_chunks = None
        self.merge_artifacts(chunks)
        self.translated_conv = Conversation(self.translated_conv)
        self.translated_conv.save_as_json(self.filename + "-cs.json")
        
        self.next(self.end)

        
    @step
    def end(self):
        print("Finished!")

if __name__ == '__main__':
    Pipeline()
