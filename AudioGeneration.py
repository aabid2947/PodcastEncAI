import noisereduce as nr
import librosa
import soundfile as sf
import os
from moviepy.editor import VideoFileClip
from pathlib import Path

def extract_audio(video_path):
    output_dir='.'
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    temp_audio_path = output_dir / f'temp_audio.wav'
    cleaned_audio_path = output_dir / f'cleaned_audio.wav'

    try:
        print(f"Processing video: {video_path}")
        with VideoFileClip(str(video_path)) as video:
            video.audio.write_audiofile(str(temp_audio_path))

        print("Audio extraction complete. Removing background noise...")
        audio, sr = librosa.load(str(temp_audio_path), sr=None)
        reduced_noise_audio = nr.reduce_noise(y=audio, sr=sr)

        sf.write(str(cleaned_audio_path), reduced_noise_audio, sr)
        print(f"Background noise removed and saved to {cleaned_audio_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        if temp_audio_path.exists():
            os.remove(temp_audio_path)

    return cleaned_audio_path



