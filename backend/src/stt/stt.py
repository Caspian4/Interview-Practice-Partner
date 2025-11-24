"""
Transcribe an audio file to text using OpenAI Whisper """
import whisper

def transcribe(audio_file_path: str) -> str:
    """
    Transcribe an audio file to text using OpenAI Whisper
    """
    if whisper is None:
        raise RuntimeError("Whisper is not installed. Install with `pip install -U openai-whisper`")

    model = whisper.load_model("base") 

    try:
        result = model.transcribe(audio_file_path)
    except FileNotFoundError as e:
        raise RuntimeError(
            "ffmpeg executable not found. Whisper requires ffmpeg to process audio. "
            "Ensure ffmpeg is installed and on your PATH."
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to transcribe audio: {e}") from e

    return result.get("text", "").strip()
