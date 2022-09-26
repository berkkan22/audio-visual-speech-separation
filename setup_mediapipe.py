import cv2
import mediapipe as mp

def setupMediapipe():
  mpDraw = mp.solutions.mediapipe.python.solutions.mpDraw = mp.solutions.mediapipe.python.solutions.drawing_utils

  # Settings for Mediapipe FaceMesh
  mpFaceMesh = mp.solutions.mediapipe.python.solutions.face_mesh
  faceMesh = mpFaceMesh.FaceMesh(max_num_faces=2)

  # Landmarks drawing specs
  landmarkDrawingSpecs = mpDraw.DrawingSpec(
    color=(244, 244, 244), thickness=1, circle_radius=0)

  landmarkConnectionSpecs = mpDraw.DrawingSpec(
    color=(0, 150, 0), thickness=1, circle_radius=0)
  
  return mpDraw, mpFaceMesh, faceMesh, landmarkDrawingSpecs, landmarkConnectionSpecs


def faceMeshProcess(faceMesh, faceMeshFrame, mpDraw, mpFaceMesh, landmarkConnectionSpecs, landmarkDrawingSpecs):
  faceMeshResult = faceMesh.process(faceMeshFrame)
  if faceMeshResult.multi_face_landmarks:
    for face in faceMeshResult.multi_face_landmarks: 
      mpDraw.draw_landmarks(faceMeshFrame, face,
                            mpFaceMesh.FACEMESH_CONTOURS,
                            connection_drawing_spec=landmarkConnectionSpecs,
                            landmark_drawing_spec=landmarkDrawingSpecs)

  return faceMeshFrame

def faceTrackLoop(cap, option):
  mpDraw, mpFaceMesh, faceMesh, landmarkDrawingSpecs, landmarkConnectionSpecs = setupMediapipe()
  
  while True:
    ref, frame = cap.read()
    
    if option == 1:
      frameMesh = faceMeshProcess(faceMesh, frame, mpDraw, mpFaceMesh, landmarkConnectionSpecs, landmarkDrawingSpecs)
      # function for faceMesh transformation ....
      cv2.imshow("Frame", frameMesh)
    elif option == 2:
      # facedetection
      print("facedetection")
    else: 
      print("Something wrong")


    if cv2.waitKey(1) == ord("q"):
      cv2.destroyAllWindows()
      break