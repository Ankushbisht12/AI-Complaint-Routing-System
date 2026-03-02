from faster_whisper import WhisperModel
import tempfile
import os
import ffmpeg

# Load model once (small model for speed)
model = WhisperModel(
    "base",
    device="cpu",        #FORCE CPU
    compute_type="int8"
)
def transcribe_audio(file_path: str):

    segments, info = model.transcribe(file_path)

    full_text = ""
    for segment in segments:
        full_text += segment.text + " "

    return full_text.strip()


def extract_audio_from_video(video_path: str):

    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_audio.close()

    (
        ffmpeg
        .input(video_path)
        .output(temp_audio.name, format="wav")
        .run(overwrite_output=True, quiet=True)
    )

    return temp_audio.name