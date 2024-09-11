import librosa
import numpy as np
from typing import Tuple, Optional
import warnings
from moviepy.editor import VideoFileClip
import noisereduce as nr
import librosa
import soundfile as sf
import os
from pathlib import Path

    
def load_and_trim_audio(audio_path: str, duration: float = 5.0) -> Tuple[np.ndarray, int]:
    """
    Load and trim audio file to specified duration.
    
    Args:
    audio_path (str): Path to the audio file.
    duration (float): Duration in seconds to trim the audio to.
    
    Returns:
    Tuple[np.ndarray, int]: Trimmed audio array and sample rate.
    """
    try:
        y, sr = librosa.load(audio_path, duration=duration)
        return y, sr
    except Exception as e:
        raise IOError(f"Error loading audio file {audio_path}: {str(e)}")

def compute_offset(y1: np.ndarray, y2: np.ndarray, sr: int) -> float:
    """
    Compute the offset between two audio arrays using cross-correlation.
    
    Args:
    y1 (np.ndarray): First audio array.
    y2 (np.ndarray): Second audio array.
    sr (int): Sample rate of the audio.
    
    Returns:
    float: Offset in seconds.
    """
    correlation = np.correlate(y1, y2, mode='full')
    lag = correlation.argmax() - (len(y2) - 1)
    return lag / sr

def get_audio_offset(audio_path1: str, audio_path2: str, duration: float = 5.0) -> Optional[float]:
    """
    Get the offset between two audio files.
    
    Args:
    audio_path1 (str): Path to the first audio file.
    audio_path2 (str): Path to the second audio file.
    duration (float): Duration in seconds to analyze from the start of each file.
    
    Returns:
    Optional[float]: Offset in seconds, or None if an error occurred.
    """
    try:
        y1, sr1 = load_and_trim_audio(audio_path1)
        y2, sr2 = load_and_trim_audio(audio_path2)
        
        if sr1 != sr2:
            warnings.warn("Sample rates of the two audio files are different. Resampling the second file.")
            y2 = librosa.resample(y2, sr2, sr1)
        breakpoint()
        offset = compute_offset(y1, y2, sr1)
        breakpoint()
        return offset
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    
# extract audios
def extract_audio(video_path, index=0):
    output_dir='.'
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    temp_audio_path = output_dir / f'temp_audio_{index}.wav'
    cleaned_audio_path = output_dir / f'cleaned_audio_{index}.wav'

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

def trim_video(video_paths,output_suffix="_Adjusted"):
    
    # extract and save audios 
    audio_paths = [extract_audio(video_paths[i],i) for i in range(0,len(video_paths))]
    
    # get the offset between the two audios
    offset = get_audio_offset(audio_paths[0], audio_paths[1])
    
    if offset is  None:
        print("Failed to compute the offset.")
 
    print(f"The offset between {audio_paths[0]}and {audio_paths[0]} is {offset:.4f} seconds.")
    if(offset==0):
        print("Both videos are in sync ")
        return video_paths
    if(offset>0):
            #  second video is lagging
            video = VideoFileClip(video_paths[0])
            output_path = f'{os.path.splitext(video_paths[0])[0] + output_suffix}.mp4'         
            video_paths[0] = output_path
    else:
            # first video is lagging
            video=VideoFileClip(video_paths[1])
            output_path = f'{os.path.splitext(video_paths[1])[0] + output_suffix}.mp4'
            video_paths[1] = output_path

    breakpoint()
    trimmed_video = video.subclip(offset)  # Trims from start_time to the end
    trimmed_video.write_videofile(output_path)
        
    
    # clean up the memory 
    for audio in audio_paths:
        os.remove(audio)
    
    # Close the video clips
    video.close()
    trimmed_video.close()
    return video_paths
    
if __name__ == '__main__':
    
    trim_video(['./videos/Full1_standardized_Adjusted.mp4','./videos/person22_standardized.MOV'])