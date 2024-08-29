# diarization.py
from pyannote.audio import Pipeline
import pickle


def Diarization(audio_path):
    # Replace 'your_token' with the actual token
    auth_token = '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'

    # Initialize the pipeline for speaker diarization
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=auth_token)
    print(audio_path)

    # Perform diarization on the combined audio file
    diarization = pipeline(audio_path)

    # Create an array to hold timestamp and speaker information
    timestamp_info = []

    # Process diarization results
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start_time = turn.start
        end_time = turn.end

        # Append speaker info with timestamp
        timestamp_info.append({
            'speaker': speaker,
            'start_time': start_time,
            'end_time': end_time
        })

    # Save the timestamp information to a file
    with open('timestamp_info.pkl', 'wb') as f:
        pickle.dump(timestamp_info, f)

    print("Speaker diarization complete and results saved.")
    return timestamp_info
