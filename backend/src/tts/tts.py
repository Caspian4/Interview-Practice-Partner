"""
Async TTS helper using edge-tts
"""
import tempfile
import os

try:
    import edge_tts
except Exception:
    edge_tts = None


def clean_for_tts(text: str) -> str:
    """
    Removes markdown bullets
    """
    text = text.replace("* ", "")
    text = text.replace("- ", "")
    text = text.replace("• ", "")
    text = text.replace("**", "")
    text = text.replace("*", "")

    return text.strip()


async def synthesize(text: str, voice: str = "en-US-AriaNeural") -> bytes:
    """Async TTS: return MP3 bytes"""

    if edge_tts is None:
        raise RuntimeError("edge-tts not installed. Install with `pip install edge-tts`")

    text = clean_for_tts(text)

    fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(tmp_path)

    try:
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    return audio_bytes
