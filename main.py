import subprocess
import os
import json
import cv2
from AudioGeneration import extract_audio
from Diariazation import perform_diarization
from IdentifySpeaker import Identify_speaker
from AdjustLag import trim_video
from CreateVideo import create_video_with_audio

def standardize_video(input_video, output_video, resolution="1280x720", frame_rate="30", codec="h264"):
    """Standardize the video parameters like resolution, frame rate, and codec."""
    command = [
        'ffmpeg', '-i', input_video,
        '-vf', f'scale={resolution}',
        '-r', frame_rate,
        '-c:v', codec,
        '-preset', 'fast',
        '-crf', '22',
        '-c:a', 'aac',
        '-b:a', '128k',
        output_video
    ]
    subprocess.run(command, check=True)
    print(f"Video {input_video} has been standardized and saved as {output_video}")

def standardize_all_videos(input_video):
    output_video = './videos/person22_standardized.MOV'
    standardize_video(input_video, output_video)
    
def add_audio_to_video(video_path, audio_path, output_path, volume_factor=20):
    """Add audio to a video file using ffmpeg and adjust the audio volume."""
    command = [
        'ffmpeg', '-y', '-i', video_path, '-i', audio_path,
        '-filter_complex', f"volume={volume_factor}",  # Adjust volume
        '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', output_path
    ]
    
    print(f"Running command to add audio with volume adjustment: {' '.join(command)}")
    subprocess.run(command, check=True)

def create_transition(frame1, frame2, num_frames, speed_factor=2):
    """Create a smooth transition between two frames."""
    transition_frames = max(1, num_frames // speed_factor)
    for i in range(transition_frames):
        alpha = i / transition_frames
        yield cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)

# def concatenate_videos_with_transitions(segment_paths, output_path, transition_frames=30):
#     """Concatenate multiple video segments into one video file with smooth transitions."""
#     caps = [cv2.VideoCapture(path) for path in segment_paths]
#     width = int(caps[0].get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(caps[0].get(cv2.CAP_PROP_FRAME_HEIGHT))
#     fps = int(caps[0].get(cv2.CAP_PROP_FPS))
    
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
#     prev_last_frame = None
    
#     for i, cap in enumerate(caps):
#         # Read the first frame of the current segment
#         ret, first_frame = cap.read()
#         if not ret:
#             continue
        
#         # If it's not the first segment, create a transition
#         if prev_last_frame is not None:
#             for transition_frame in create_transition(prev_last_frame, first_frame, transition_frames):
#                 out.write(transition_frame)
        
#         # Write the rest of the frames from the current segment
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break
#             out.write(frame)
        
#         # Store the last frame for the next transition
#         cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1)
#         ret, prev_last_frame = cap.read()
    
    # for cap in caps:
    #     cap.release()
    
    # out.release()


# Main function
def main():\
    # Replace with your actual token
    AUTH_TOKEN = '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'
    
    # Enter Video paths
    Ind_video_paths = ['./videos/Full1_standardized.MOV', './videos/person22_standardized.MOV']

    # Extract audio from video 
    Adjusted_video_paths = trim_video(Ind_video_paths)
    
    # extract audio for diariazation
    audio_path = extract_audio(Adjusted_video_paths[0])
    
    # Perform Diariazation
    timestamp_info =  perform_diarization(audio_path=audio_path,auth_token=AUTH_TOKEN)
    
    # Map video and speaker 
    enhanced_timestamp_info = Identify_speaker(Adjusted_video_paths,timestamp_info)
    
    # Load JSON data
    with open('time_stamp_udemi.json', 'r') as f:
        enhanced_timestamp_info = json.load(f)

    # Create video with audio
    create_video_with_audio(enhanced_timestamp_info, audio_path)

    # Clean up temporary audio file
    os.remove(audio_path)

if __name__ == '__main__':
    main()
