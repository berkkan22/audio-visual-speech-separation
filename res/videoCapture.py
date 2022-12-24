from multiprocessing import Process
import cv2
import numpy as np
import mediapipe as mp


FPS = 25
VIDEO_BUFFER_SIZE = 64
FONT = cv2.FONT_HERSHEY_PLAIN
MAX_NUM_FACES = 2
GAB_BETWEEN_LIP = 20


# or make it as a flatted shape?


class CaptureVideo(Process):
  def __init__(self, queue, streamID):
  # def __init__(self, streamID):
    super().__init__()
    self.queue = queue
    self.streamID = streamID
    
    self.cap = cv2.VideoCapture(self.streamID)

    
    self.videoBufferFromThePast = np.zeros(VIDEO_BUFFER_SIZE)

    
    self.mpDraw = mp.solutions.mediapipe.python.solutions.drawing_utils
    self.mpFaceMesh = mp.solutions.mediapipe.python.solutions.face_mesh
    
    self.faceMesh = self.mpFaceMesh.FaceMesh(max_num_faces=MAX_NUM_FACES)

    self.landmarkDrawingSpecs = self.mpDraw.DrawingSpec(
      color=(244, 244, 244), thickness=1, circle_radius=0)

    self.landmarkConnectionSpecs = self.mpDraw.DrawingSpec(
      color=(0, 150, 0), thickness=1, circle_radius=0)
    
    self.detectFace0 = 1

    
    
  def run(self):
    print("Started video capture process")
    self.cap.set(cv2.CAP_PROP_FPS, FPS) # set FPS to 25 to sync it good with the audio_buffer
    
    if(self.cap.isOpened()):
      print("Started video capture")
      while True:
        ref, frame = self.cap.read()

        # the queue will always be empty because in the sync Process there we get the element
        
        # ein element im buffer ist ein frame
        self.videoBufferFromThePast[VIDEO_BUFFER_SIZE-1::] = frame
        temp = self.videoBufferFromThePast[1::]
        self.videoBufferFromThePast = np.append(temp, np.zeros(1))
        print(self.videoBufferFromThePast)
        self.queue.put(self.videoBufferFromThePast)
                
        try:
          # TODO: how to get the frame from the functions
          self.faceMeshDetection(frame)
        except:
          print("FaceMesh could not be detected")

        cv2.imshow("Frame", frame)
        
        if cv2.waitKey(1) == ord("q"):
          break
    
    print("Capture device is could not be open")


  def getFrame(self):
    return self.queue

  def faceMeshDetection(self, frame):
    height = frame.shape[0]
    width = frame.shape[1]

    frame = cv2.flip(frame, 1)
    
    # Copy frame to manipulate it
    # TODO:
    lipFrame = frame.copy()
    faceMeshFrame = frame.copy()

    # create RGB frame because mediapipe use RGB
    frameRGB = cv2.cvtColor(faceMeshFrame, cv2.COLOR_BGR2RGB)
    
    # FaceMesh with 468 points
    faceMeshResult = self.faceMesh.process(frameRGB)
    if faceMeshResult.multi_face_landmarks:
      for i in range(0, len(faceMeshResult.multi_face_landmarks)):
        if faceMeshResult.multi_face_landmarks[i]:
          
          # Puts face number
          cv2.putText(faceMeshFrame, "Face " + str(i), (int(faceMeshResult.multi_face_landmarks[i].landmark[0].x * width - 100), int(faceMeshResult.multi_face_landmarks[i].landmark[0].y * height - 100)), FONT, 1, (0, 0, 255), 1)
          
          # This code checks if the first face detected is on the left side of the screen
          # and if the detectFace0 boolean is true
          if(faceMeshResult.multi_face_landmarks[i].landmark[0].x * width < width // 2 and self.detectFace0):
            self.mpDraw.draw_landmarks(faceMeshFrame, faceMeshResult.multi_face_landmarks[i], 
                                  self.mpFaceMesh.FACEMESH_CONTOURS, 
                                  connection_drawing_spec=self.landmarkConnectionSpecs,
                                  landmark_drawing_spec=self.landmarkDrawingSpecs)
            
            self.drawRectAroundLips(lipFrame, faceMeshResult.multi_face_landmarks[i].landmark)
          elif(faceMeshResult.multi_face_landmarks[i].landmark[0].x * width > width // 2 and not self.detectFace0):
            self.mpDraw.draw_landmarks(faceMeshFrame, faceMeshResult.multi_face_landmarks[i], 
                                  self.mpFaceMesh.FACEMESH_CONTOURS, 
                                  connection_drawing_spec=self.landmarkConnectionSpecs,
                                  landmark_drawing_spec=self.landmarkDrawingSpecs)

            self.drawRectAroundLips(lipFrame, faceMeshResult.multi_face_landmarks[i].landmark)


  def faceDetection(frame):
    pass

  def cropLips(self, frame, minXWithGap, maxXWithGap, minYWithGap, maxYWithGap):
    """Crops the lips from the frame

    Args:
        frame (_type_): video frame
        minXWithGap (int): minimum x value of the lips
        maxXWithGap (int): maximum x value of the lips
        minYWithGap (int): minimum y value of the lips
        maxYWithGap (int): maximum y value of the lips

    Returns:
        _type_: returns the cropped lips
    """
    frame = frame[minYWithGap:maxYWithGap, minXWithGap:maxXWithGap]
    cropLipResized = cv2.resize(frame, (300, 300))
    return cropLipResized


  def drawRectAroundLips(self, frame, landmarks):
    """Draws a rectangle around the lips and 
        and calls the function [cropLips] to crop the lips
        and show it in a new window

    Args:
        frame (_type_): video frame
        landmarks (_type_): the landmarks of the face
    """
    width = frame.shape[1]
    height = frame.shape[0]
    
    minX = width
    maxX = 0
    minY = height
    maxY = 0 
    
    minXWithGap = 0
    maxXWithGap = 0
    minYWithGap = 0
    maxYWithGap = 0
    
    FACEMESH_LIPS_TUPLE = list(self.mpFaceMesh.FACEMESH_LIPS)
    FACEMESH_LIPS_LIST = []
    for point in FACEMESH_LIPS_TUPLE:
      FACEMESH_LIPS_LIST.append(point[0])
      FACEMESH_LIPS_LIST.append(point[1])
      
    for point in FACEMESH_LIPS_LIST:
      lipPoints = landmarks[point]
      x = lipPoints.x * width
      y = lipPoints.y * height
      
      if x < minX:
        minX = int(x)
      if x > maxX:
        maxX = int(x)
      if y < minY:
        minY = int(y)
      if y > maxY:
        maxY = int(y)
      
    minXWithGap = minX - GAB_BETWEEN_LIP
    maxXWithGap = maxX + GAB_BETWEEN_LIP
    minYWithGap = minY - GAB_BETWEEN_LIP
    maxYWithGap = maxY + GAB_BETWEEN_LIP
    
    cv2.rectangle(frame, (minXWithGap, minYWithGap), 
                  (maxXWithGap, maxYWithGap), (255, 0, 0), 2)
    
    cropedLips = self.cropLips(frame, minXWithGap, maxXWithGap, minYWithGap, maxYWithGap)
    
    # TODO:
    cv2.imshow("Lips", frame)
    cv2.imshow("CropedLips", cropedLips)

