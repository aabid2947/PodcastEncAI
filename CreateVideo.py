import os
import cv2
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

def concatenate_videos_with_transitions(segment_paths, output_path, transition_frames=15):
    # Use ffmpeg to concatenate the segments with transitions
    command = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', 'concat_list.txt',
        '-c', 'copy', output_path
    ]
    
    # Create a 'concat_list.txt' file with the input video paths and transition commands
    with open('concat_list.txt', 'w') as f:
        for i, path in enumerate(segment_paths):
            f.write(f"file '{path}'\n")
            if i < len(segment_paths) - 1:
                f.write(f"duration {transition_frames/30.0}\n") # Assuming 30 fps
                f.write("filter_complex \"[0:v][1:v]xfade=transition=fade:duration={transition_frames/30.0}[outv]\"\n")
    
    subprocess.run(command, check=True)

def combine_video_audio(video_segment, audio_segment, output_path):
    """Combine video and audio segments into a single video file."""
    
    command = [
        'ffmpeg', '-y', '-i', video_segment, '-i', audio_segment,
        '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', output_path
    ]
    subprocess.run(command, check=True)
    print(f"Combined video and audio saved as {output_path}")

def extract_audio_segment(audio_path, start_time, end_time, output_audio_path):
    """Extract an audio segment from a given audio file."""
    command = [
        'ffmpeg', '-y', '-i', audio_path,
        '-ss', str(start_time), '-to', str(end_time),
        '-c:a', 'aac', '-b:a', '128k', output_audio_path
    ]
    subprocess.run(command, check=True)
    print(f"Audio segment from {start_time} to {end_time} has been saved as {output_audio_path}")

def extract_video_segment(video_path, start_time, end_time, output_path):
    """Extract a segment from a video file and save it to output_path."""
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))
    
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame_count > (end_frame - start_frame):
            break
        out.write(frame)
        frame_count += 1
    cap.release()
    out.release()

def extract_video_and_audio_segments(video_path, audio_path, start_time, end_time, video_output_path, audio_output_path):
    """Extract video and audio segments and combine them into a single segment."""
    extract_video_segment(video_path, start_time, end_time, video_output_path)
    extract_audio_segment(audio_path, start_time, end_time, audio_output_path)
    
    # Combine video and audio segment
    combined_output_path = f'./temp/combined_segment_{os.path.basename(video_output_path)}'
    combine_video_audio(video_output_path, audio_output_path, combined_output_path)
    return combined_output_path

def extract_and_combine_segment(segment, audio_path):
    """Extract and combine video and audio segments, to be used in parallel processing."""
    start_time = segment['start_time']
    end_time = segment['end_time']
    video_path = segment['video_path']
    
    
    # Define temporary paths for video and audio segments
    temp_video_segment_path = f'./temp/temp_segment_{segment["index"]}.mp4'
    temp_audio_segment_path = f'./temp/temp_audio_{segment["index"]}.aac'
    
    # Extract and combine video and audio segments
    combined_segment_path = extract_video_and_audio_segments(
        video_path, audio_path, start_time, end_time,
        temp_video_segment_path, temp_audio_segment_path
    )
    
    return combined_segment_path

def create_video_with_audio(timestamp_info, audio_path):
    """Create a final video with smooth transitions and audio using OpenCV and ffmpeg."""
    segment_paths = []
    temp_files = []

    try:
        # Prepare segments for parallel processing
        segments = [{'start_time': seg['start_time'], 'end_time': seg['end_time'],
                     'video_path': seg['video_path'], 'index': i}
                    for i, seg in enumerate(timestamp_info)]
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor() as executor:
            future_to_segment = {executor.submit(extract_and_combine_segment, seg, audio_path): seg for seg in segments}
            
            for future in as_completed(future_to_segment):
                segment = future_to_segment[future]
                try:
                    combined_segment_path = future.result()
                    segment_paths.append(combined_segment_path)
                except Exception as exc:
                    print(f'Segment {segment["index"]} generated an exception: {exc}')
        
        # Concatenate all segments with transitions
        final_video_path = './output/final_video.mp4'
        concatenate_videos_with_transitions(segment_paths, final_video_path)
        
        # Optionally add audio to the final video if needed
        final_video_with_audio_path = './output/final_video_with_audio.mp4'
        # add_audio_to_video(final_video_path, audio_path, final_video_with_audio_path)
    
    finally:
        # Clean up temporary files
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)