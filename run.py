from TTS.api import TTS
import modal
from tqdm import tqdm
from model.conversation import Conversation, ConversationChunk
import os

# CACHE_PATH = "/root/model_cache"
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
INPUT_DIR = "/data/input"
OUTPUT_DIR = "/data/output"

stub = modal.Stub("podcast-translator")


def download_model_weights() -> None:
    from TTS.api import TTS

    TTS(MODEL_NAME,  progress_bar=False)


image = (
    modal.Image.from_registry("pytorch/pytorch:2.2.1-cuda11.8-cudnn8-runtime")
    .env({"COQUI_TOS_AGREED": "1"})
    .pip_install(
        "tts>=0.22.0",
    )
    .run_function(download_model_weights)
)
vol = modal.Volume.from_name("podcast-translator", create_if_missing=True)


def format_name(name: str) -> str:
    formated_name = name.lower()
    return formated_name.replace(" ", "-")


def output_filename(chunk: ConversationChunk):
    return OUTPUT_DIR + "/" + format_name(chunk.speaker) + "-" + str(chunk.ts_sortable)

@stub.function(
    gpu="any",
    image=image,
    volumes={"/data": vol},
    retries=1,
    timeout=3600,
)
def generate():
    from TTS.api import TTS
    tts = TTS(MODEL_NAME,  progress_bar=False, gpu=True)

    conversation = Conversation()
    conversation.from_json(INPUT_DIR + "/serhii-plokhy-transcript-cs.json")
    lex_chunks = conversation.get_speaker_chunks("Lex Fridman")

    for chunk in tqdm(lex_chunks):
        if os.path.exists(output_filename(chunk)):
            continue
        
        tts.tts_to_file(text=chunk.text,
                        file_path=output_filename(chunk),
                        speaker_wav="/data/input/lex_voice.wav",
                        language="cs")
        vol.commit()


