import logging
import os
import uuid

from datetime import datetime
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

ELEVEN_API_KEY = os.environ["ELEVEN_API_KEY"]

if not ELEVEN_API_KEY:
    raise ValueError("ELEVEN_API_KEY environment variable not set")

client = ElevenLabs(
    api_key=ELEVEN_API_KEY,
)


def text_to_speech_file(text: str) -> str:
    """
    Converts text to speech and saves the output as an MP3 file.

    This function uses a specific client for text-to-speech conversion. It configures
    various parameters for the voice output and saves the resulting audio stream to an
    MP3 file with a unique name.

    Args:
        text (str): The text content to convert to speech.

    Returns:
        str: The file path where the audio file has been saved.
    """
    # Calling the text_to_speech conversion API with detailed parameters
    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam pre-made voice
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2",  # use the turbo model for low latency, for other languages use the `eleven_multilingual_v2`
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    # Generating a unique file name for the output MP3 file
    save_file_path = os.path.join(folder, f"podcast_audio_{current_date}.mp3")

    # Writing the audio stream to the file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"A new audio file was saved successfully at {save_file_path}")

    # Return the path of the saved audio file
    return save_file_path


if __name__ == "__main__":
    current_date = datetime.now().strftime('%Y%m%d')
    folder = 'audios'
    os.makedirs(folder, exist_ok=True)
    logging.info(f"Folder created at: {folder}")
    # with open(f'scripts/{current_date}/podcast_script_{current_date}.txt', 'r') as file:
    #     data = file.read()
    # text_to_speech_file(data)
    with open(f'test.txt', 'r') as file:
         data = file.read()
    text_to_speech_file(data)