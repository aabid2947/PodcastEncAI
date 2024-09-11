import urllib.request
import bz2
import cv2
import dlib
import os
import json

def enhance_timestamps(timestamp_info):
    """Enhance timestamps by matching the end time of each segment to the start time of the next segment."""
    enhanced_info = []
    for i, segment in enumerate(timestamp_info):
        if i < len(timestamp_info) - 1:
            next_start_time = timestamp_info[i + 1]['start_time']
            segment['end_time'] = next_start_time
        enhanced_info.append(segment)
    return enhanced_info

def download_shape_predictor():
    print("Downloading shape predictor file...")
    url = "https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2"
    file_path = "shape_predictor_68_face_landmarks.dat.bz2"
    urllib.request.urlretrieve(url, file_path)
    
    print("Extracting shape predictor file...")
    with bz2.BZ2File(file_path) as fr, open("shape_predictor_68_face_landmarks.dat", "wb") as fw:
        fw.write(fr.read())
    os.remove(file_path)
    print("Shape predictor file is ready.")

def detect_lip_movement(video_path, timestamp_info):
    speaking_times = []
    print('here')
    
    # Check if shape predictor file exists, if not, download it
    if not os.path.exists("shape_predictor_68_face_landmarks.dat"):
        download_shape_predictor()

    # Load face detector and facial landmark predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    print('here')

    for segment in timestamp_info:
        start_time = segment['start_time']
        end_time = segment['end_time']
        
        
        
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Unable to open video file '{video_path}'")
            return

        # Calculate the frame range for the current segment
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        max_frames = int(frame_rate * (end_time - start_time))
        speaking_time = 0

        prev_mouth_height = 0
        speaking_threshold = 2  # Adjust this value based on your needs
        print('here')

        frame_num = 0
        while cap.isOpened() and frame_num < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = detector(gray)

            for face in faces:
                # Get facial landmarks
                landmarks = predictor(gray, face)

                # Get mouth landmarks
                mouth_top = landmarks.part(62).y
                mouth_bottom = landmarks.part(66).y
                mouth_height = mouth_bottom - mouth_top

                # Check if mouth height has changed significantly (indicating speech)
                if abs(mouth_height - prev_mouth_height) > speaking_threshold:
                    speaking_time += 1

                prev_mouth_height = mouth_height
            # Display the frame with bounding box
            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
               break
            frame_num += 1

        cap.release()
        cv2.destroyAllWindows()
        speaking_times.append(speaking_time)

    return speaking_times

def Identify_speaker(video_paths,timestamp_info):
    # Usage
    Ind_videos_path = video_paths

    # Load JSON data
    with open('time_stamp.json', 'r') as f:
        timestamp_info = json.load(f)
    timestamp_info = enhance_timestamps(timestamp_info=timestamp_info)
    
    Speakers={}
    for i in timestamp_info:
        if(i['speaker'] not in Speakers ):Speakers[i['speaker']]={f'{video_path}':0 for video_path in Ind_videos_path}
        
    # Calculate speaking time for each video
    speaking_times = [detect_lip_movement(video_path, timestamp_info=timestamp_info) for video_path in Ind_videos_path]

        
    for i, segment in enumerate(timestamp_info):
        segment_speaking_times = [speaking_times[v_idx][i] for v_idx in range(len(Ind_videos_path))]
        best_video_idx = segment_speaking_times.index(max(segment_speaking_times))
        Speakers[f'{segment["speaker"]}'][f'{Ind_videos_path[best_video_idx]}']+=1
    print(Speakers)
    
        
        
    if Speakers['SPEAKER_00'][Ind_videos_path[0]] <Speakers['SPEAKER_01'][Ind_videos_path[0]]:
            Speakers['SPEAKER_00'] = Ind_videos_path[1]
            Speakers['SPEAKER_01'] = Ind_videos_path[0]  
    else:
            Speakers['SPEAKER_01'] = Ind_videos_path[1]
            Speakers['SPEAKER_00'] = Ind_videos_path[0]
        
    # Update timestamp_info based on index_mapping
    for i, segment in enumerate(timestamp_info):
            segment['video_path'] = Speakers[segment['speaker']]
            
            

    # Save the updated timestamp info
    output_file = 'time_stamp.json'
    with open(output_file, 'w') as f:
        json.dump(timestamp_info, f, indent=4)
    
    return timestamp_info

if __name__ == '__main__':
    Identify_speaker(['./videos/Firoz_standardized.mp4', './videos/Ahmad_standardized.mp4'])