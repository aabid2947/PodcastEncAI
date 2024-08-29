import pickle
import subprocess
import os
from Diariazation import Diarization
from AudioGeneration import video_to_audio

# Define file paths
video_paths = {
    'SPEAKER_01': './videos/person1.mp4',
    'SPEAKER_02': './videos/person2.mp4',
    'SPEAKER_00': './videos/Full.mp4'
}
output_video = './videos/final_video_with_audio.mp4'
temp_video_file = './videos/temp_final_video.mp4'

# Load timestamp information from pickle file
# uncommnet after saving diariazation result
# with open('timestamp_info.pkl', 'rb') as f:
#     timestamp_info = pickle.load(f)

def enhance_timestamps(timestamp_info):
    """Enhance timestamps by matching end time of each segment to the start time of the next segment."""
    enhanced_info = []
    for i, segment in enumerate(timestamp_info):
        if i < len(timestamp_info) - 1:
            next_start_time = timestamp_info[i + 1]['start_time']
            # Update end_time of current segment to match start_time of next segment
            segment['end_time'] = next_start_time
        enhanced_info.append(segment)
    return enhanced_info

def create_video_with_audio(timestamp_info, audio_path):
    """Create a final video with audio using ffmpeg."""
    segments_file = 'segments.txt'
    
    # Create or overwrite segments file
    with open(segments_file, 'w') as f:
        for i, segment in enumerate(timestamp_info):
            speaker = segment['speaker']
            start_time = segment['start_time']
            end_time = segment['end_time']
            segment_duration = end_time - start_time

            temp_segment_file = f'temp_segment_{i}.mp4'
            # Use ffmpeg to cut the segment from the video
            command = [
                'ffmpeg', '-y', '-i', video_paths[speaker], '-ss', str(start_time), '-to', str(end_time),
                '-c:v', 'libx264', '-c:a', 'aac', '-loglevel', 'info', temp_segment_file
            ]
            print(f"Running command to extract segment: {command}")
            subprocess.run(command, check=True)

            # Add segment to the file list
            f.write(f"file '{temp_segment_file}'\n")
    
    # Concatenate all video segments
    final_video_file = 'temp_final_video.mp4'
    command = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', segments_file, '-c', 'copy', '-loglevel', 'info', final_video_file
    ]
    print(f"Running command to concatenate segments: {command}")
    subprocess.run(command, check=True)

    # Add audio to the final video
    command = [
        'ffmpeg', '-y', '-i', final_video_file, '-i', audio_path, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', '-loglevel', 'info', output_video
    ]
    print(f"Running command to add audio: {command}")
    subprocess.run(command, check=True)

    # Clean up temporary files
    os.remove(segments_file)
    for i in range(len(timestamp_info)):
        os.remove(f'temp_segment_{i}.mp4')

    print("Final video with audio created successfully.")

def main():
    video_path = './videos/Full.mp4'
    
    # Extract audio from video 
    audio_path = video_to_audio(video_path)
    
    # Classify different speaker in the video 
    # Uncomment if Diarization should be performed again
    timestamp_info = Diarization(audio_path=audio_path)

    # Enhance timestamps
    enhanced_timestamp_info = enhance_timestamps(timestamp_info)

    # Create video with audio
    create_video_with_audio(enhanced_timestamp_info, audio_path)

    # Clean up temporary audio file
    os.remove(audio_path)

if __name__ == '__main__':
    main()
