# -*- coding: utf-8 -*-
"""
Face Detector with OpenCV (Alternative to MediaPipe).
Uses Haar Cascade for real-time face detection from webcam.
"""

import cv2

# Load pre-trained Haar Cascade classifier for faces
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Open webcam (0 for default)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Convert to grayscale for faster detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces (scaleFactor=1.1, minNeighbors=5 for balance accuracy/speed)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Draw rectangles around detected faces
    for (x, y, w, h) in faces:
        # Bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)
        
        # Proxy confidence (based on detection scale; higher = more confident)
        confidence = round(100 - (w * h / 10000), 2)  # Simple heuristic
        label = f'Face ({confidence}%)'
        
        # Add label
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # Display the frame
    cv2.imshow('Face Detection with OpenCV', frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()