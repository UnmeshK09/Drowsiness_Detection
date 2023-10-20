import cv2
import dlib
import pyttsx3
from scipy.spatial import distance
import socket

# Initialize pyttsx3 for alert audio
engine = pyttsx3.init()# Set up the camera (0 or 1 for the camera index)
cap = cv2.VideoCapture(0)
# Load face detector and landmarks predictor
face_detector = dlib.get_frontal_face_detector()
dlib_facelandmark = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Set up the socket connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 12345))  # Change the IP address and port as needed

# Function to calculate the aspect ratio for the eyes
def Detect_Eye(eye):
    poi_A = distance.euclidean(eye[1], eye[5])
    poi_B = distance.euclidean(eye[2], eye[4])
    poi_C = distance.euclidean(eye[0], eye[3])
    aspect_ratio_Eye = (poi_A + poi_B) / (2 * poi_C)
    return aspect_ratio_Eye


# Initialize dynamic threshold variables
baseline_EAR = None
CONSECUTIVE_FRAMES_THRESHOLD = 2  # Adjust as needed
frame_counter = 0

while True:
    # Capture a frame from the camera
    _, frame = cap.read()
    gray_scale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector(gray_scale)

    for face in faces:
        face_landmarks = dlib_facelandmark(gray_scale, face)
        leftEye = []
        rightEye = []

        # Points allocation for the left eyes in .DAT file (42 to 47)
        for n in range(42, 48):
            x = face_landmarks.part(n).x
            y = face_landmarks.part(n).y
            rightEye.append((x, y))
            next_point = n + 1
            if n == 47:
                next_point = 42
            x2 = face_landmarks.part(next_point).x
            y2 = face_landmarks.part(next_point).y
            cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)

        # Points allocation for the right eyes in .DAT file (36 to 41)
        for n in range(36, 42):
            x = face_landmarks.part(n).x
            y = face_landmarks.part(n).y
            leftEye.append((x, y))
            next_point = n + 1
            if n == 41:
                next_point = 36
            x2 = face_landmarks.part(next_point).x
            y2 = face_landmarks.part(next_point).y
            cv2.line(frame, (x, y), (x2, y2), (255, 255, 0), 1)

        # Calculate the aspect ratio
        right_Eye = Detect_Eye(rightEye)
        left_Eye = Detect_Eye(leftEye)
        Eye_Rat = (left_Eye + right_Eye) / 2

        # Update baseline_EAR if it's None (first frame)
        if baseline_EAR is None:
            baseline_EAR = Eye_Rat

        # Calculate dynamic threshold as a percentage of baseline_EAR
        threshold = baseline_EAR * 0.8  # Adjust the percentage as needed

        # Adjust the threshold based on your testing
        if Eye_Rat < threshold:
            frame_counter += 1
            if frame_counter >= CONSECUTIVE_FRAMES_THRESHOLD:
                cv2.putText(frame, "DROWSINESS DETECTED", (50, 100),
                            cv2.FONT_HERSHEY_PLAIN, 2, (21, 56, 210), 3)
                cv2.putText(frame, "ALERT", (50, 450),
                            cv2.FONT_HERSHEY_PLAIN, 2, (21, 56, 212), 3)
                s.send(b'Drowsy')  # Send the drowsy flag over the socket
                print("Driver is drowsy!")  # Print for debugging
                frame_counter = 0
        else:
            frame_counter = 0
            s.send(b'Not drowsy')  # Send the not drowsy flag over the socket

    cv2.imshow("Drowsiness DETECTOR IN OPENCV2", frame)
    key = cv2.waitKey(1)  # Adjust the delay as needed
    if key == 27:  # Press 'Esc' to exit the loop
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()