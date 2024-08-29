# video_to_audio.py
import ffmpeg

def video_to_audio(video_path):
    audio_path = 'Full.wav'
    print(video_path)
    # Extract and convert audio from individual videos
   
    ffmpeg.input(video_path).output(
        audio_path,
        format='wav',   # Ensure WAV format
        ac=1,           # Convert to mono
        ar='16000'      # Set sample rate to 16kHz
    ).run()

    print("Audio extraction and conversion complete.")
    return audio_path
