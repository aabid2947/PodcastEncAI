Video Processing with Speaker Diarization
Description
    This project processes video files to create a final video with enhanced audio, where speaker diarization is applied to segment the video based on who is speaking. The final output combines video segments corresponding to different speakers and overlays the audio. The project uses speaker diarization to identify and segment different speakers and integrates FFmpeg for video and audio processing.

Technologies Used
    Python: Programming language used for scripting.
    pyannote.audio: Library for speaker diarization.
    FFmpeg: Tool for handling video and audio extraction, conversion, and concatenation.
    pickle: Python module for serializing and deserializing data.
Getting Started
    Prerequisites:
        Ensure you have the following installed:
        Python 3.x
        FFmpeg
        Required Python libraries (pyannote.audio, ffmpeg-python, pickle)

    Installation:
        Clone the Repository
        git clone https://github.com/yourusername/your-repository.git
        cd your-repository
        Install Python Dependencies

You need to install the required Python libraries. Create a virtual environment and install the dependencies:

    bash
    python -m venv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`
    pip install pyannote.audio ffmpeg-python
    Running the Project
    Prepare Video Files

Place your video files in the ./videos directory. The files should be named as follows:

person1.mp4 (for SPEAKER_01)
person2.mp4 (for SPEAKER_02)
Full.mp4 (for SPEAKER_00)

Run Speaker Diarization

If you need to perform speaker diarization again, uncomment the relevant line in main() of the video_processing.py script:


timestamp_info = Diarization(audio_path=audio_path)
This step will generate a timestamp_info.pkl file with the speaker diarization results.

Extract Audio and Create Final Video

Execute the main script:
    python main.py

This script will:
    Extract audio from the full video.
    Perform speaker diarization (if not previously done).
    Enhance timestamps for video segments.
    Create the final video with audio.

Output:
    The final video with audio will be saved as ./videos/final_video_with_audio.mp4.

Script Overview
    video_processing.py
    enhance_timestamps(timestamp_info): Adjusts timestamps to ensure continuity between video segments.
    create_video_with_audio(timestamp_info, audio_path): Creates a final video by cutting segments from the input videos, concatenating them, and overlaying the audio.
    main(): Coordinates the workflow, including extracting audio, performing diarization, and creating the final video.
    diarization.py
    Diarization(audio_path): Uses pyannote.audio to perform speaker diarization on the audio file and saves the results in a pickle file.
    video_to_audio.py
    video_to_audio(video_path): Extracts audio from the video and converts it to WAV format.
Troubleshooting
    Video Freezes: Ensure that the video segments are properly processed and concatenated. Check the FFmpeg logs for any errors or warnings.
    Library Issues: Ensure all required libraries are installed and up-to-date.
