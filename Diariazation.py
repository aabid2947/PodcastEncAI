import json
from pathlib import Path
from pyannote.audio import Pipeline

def perform_diarization(audio_path='Full_cleaned.wav', auth_token=None):
    """Perform speaker diarization on an audio file."""
    if auth_token is None:
        raise ValueError("Authentication token is required")

    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Initialize pipeline
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=auth_token)
    print(f"Generating diarization for {audio_path}")

    # Perform diarization
    diarization = pipeline(str(audio_path))

    # Process results
    timestamp_info = [
        {
            'speaker': speaker,
            'start_time': turn.start,
            'end_time': turn.end
        }
        for turn, _, speaker in diarization.itertracks(yield_label=True)
    ]

    # Save results
    output_file = audio_path.with_name('time_stamp.json')
    with open(output_file, 'w') as f:
        json.dump(timestamp_info, f, indent=4)

    print(f"Speaker diarization complete. Results saved to {output_file}")
    return diarization

if __name__ == '__main__':
    # Replace with your actual token
    AUTH_TOKEN = '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'
    try:
        perform_diarization(auth_token=AUTH_TOKEN)
    except Exception as e:
        print(f"An error occurred: {e}")