from pathlib import Path
from openai import OpenAI

# OpenAi API
apikey = 'sk-'

def read_text_from_file(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

if __name__ == "__main__":

    text_input = "../../input_poems/New_Orleans_Function_by_Michael_Collins.txt"
    text_input = read_text_from_file(text_input)

    client = OpenAI(api_key=apikey)
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text_input,
    )
    response.stream_to_file(speech_file_path)

