import cv2
import mediapipe as mp
import time

global previousFPSTime
previousFPSTime = 0

def calculateFPS():
  global previousFPSTime
  previousFPSTime = previousFPSTime
  # calculate FPS
  currentFPSTime = time.time()
  fps = 1 / (currentFPSTime - previousFPSTime)
  previousFPSTime = currentFPSTime
  fps = "FPS: " + str(int(fps))
  return fps

FONT = cv2. FONT_HERSHEY_PLAIN
GAP_BETWEEN_LIP = 20

mpDraw = mp.solutions.mediapipe.python.solutions.mpDraw = mp.solutions.mediapipe.python.solutions.drawing_utils


# Settings for Mediapipe FaceDetection 
mpFaceDetection = mp.solutions.mediapipe.python.solutions.face_detection
faceDetection = mpFaceDetection.FaceDetection(
  model_selection=0, min_detection_confidence=0.5)

# Landmarks drawing specs
landmarkDrawingSpecs = mpDraw.DrawingSpec(
  color=(244, 244, 244), thickness=1, circle_radius=0)

landmarkConnectionSpecs = mpDraw.DrawingSpec(
  color=(0, 150, 0), thickness=1, circle_radius=0)

# Take webcam as camera
cap = cv2.VideoCapture(0)

while True:
  # Limit FPS to 30
  cap.set(cv2.CAP_PROP_FPS, 30)

  ref, frame = cap.read()
  height = frame.shape[0]
  width = frame.shape[1]

  frame = cv2.flip(frame, 1)

  frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

  faceDetectionFrame = frame.copy()

  # Face detection
  faceDetectionResult = faceDetection.process(frameRGB)
  if faceDetectionResult.detections:
    for detected in faceDetectionResult.detections:
      mpDraw.draw_detection(faceDetectionFrame, detected)


  fps = calculateFPS()
  
  cv2.putText(faceDetectionFrame, fps, (7, 20), FONT, 1.5, (100, 255, 0), 1)

  cv2.imshow("Frame", faceDetectionFrame)

  if cv2.waitKey(1) == ord("q"):
    break

cap.release()
cv2.destroyAllWindows()

