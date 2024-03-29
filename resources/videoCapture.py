from multiprocessing import Process
import cv2
# import acapture
import mediapipe as mp
import time
import numpy as np
from global_variables import *

class CaptureVideo(Process):
    def __init__(self, face1Queue, face2Queue, streamID):
        super().__init__()
        print("VideoCapture: init")
        self.face1Queue = face1Queue
        self.face2Queue = face2Queue

        self.streamID = streamID

    def run(self):
        print("VideoCapture: run")
        self.mpDraw = mp.solutions.mediapipe.python.solutions.drawing_utils
        self.mpFaceMesh = mp.solutions.mediapipe.python.solutions.face_mesh

        self.faceMesh = self.mpFaceMesh.FaceMesh(max_num_faces=2)

        self.landmarkDrawingSpecs = self.mpDraw.DrawingSpec(
            color=(244, 244, 244), thickness=1, circle_radius=0)

        self.landmarkConnectionSpecs = self.mpDraw.DrawingSpec(
            color=(0, 150, 0), thickness=1, circle_radius=0)

        self.detectFace0 = 1

        cap = cv2.VideoCapture(self.streamID)
        # cap = cv2.VideoCapture("res/video540p.mp4")
        # cap = acapture.open(self.streamID) # , acapture.CAP_FFMPEG, 0)

        # print("VideoCapture: ", cap.isOpened())

        while(True):
            # Capture frame-by-frame
            cap.set(cv2.CAP_PROP_FPS, FPS_RATE)
            ref, frame = cap.read()
            # frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)

            height = frame.shape[0]
            width = frame.shape[1]

            resized = cv2.resize(
                frame, (width // 2, height // 2), interpolation=cv2.INTER_AREA)

            faceMeshDetectionFrame, landmarks = self.faceMeshDetection(resized)

            croppedLipsFrame1 = np.zeros((ROI_FRAME_HEIGHT, ROI_FRAME_WIDHT, ROI_FRAME_CHANNELS), dtype=np.uint8)
            croppedLipsFrame2 = np.zeros((ROI_FRAME_HEIGHT, ROI_FRAME_WIDHT, ROI_FRAME_CHANNELS), dtype=np.uint8)
            rectAroundLipsFrame1 = np.zeros((height, width, ROI_FRAME_CHANNELS), dtype=np.uint8)
            rectAroundLipsFrame2 = np.zeros((height, width, ROI_FRAME_CHANNELS), dtype=np.uint8)

            if(faceMeshDetectionFrame is not None and landmarks is not None):
                for i in range(0, len(landmarks)):
                    if(i == 0 and not (landmarks[i].landmark[0].x * width < width // 2)):
                        croppedLipsFrame1 = np.zeros((ROI_FRAME_HEIGHT, ROI_FRAME_WIDHT, ROI_FRAME_CHANNELS), dtype=np.uint8)

                    if(i == 1 and not (landmarks[i].landmark[0].x * width > width // 2)):
                        croppedLipsFrame2 = np.zeros((ROI_FRAME_HEIGHT, ROI_FRAME_WIDHT, ROI_FRAME_CHANNELS), dtype=np.uint8)

                    if(landmarks[i].landmark[0].x * width < width // 2):
                        rectAroundLipsFrame1, croppedLipsFrame1 = self.drawRectAroundLips(
                            resized, landmarks[i].landmark)

                    if(landmarks[i].landmark[0].x * width > width // 2):
                        rectAroundLipsFrame2, croppedLipsFrame2 = self.drawRectAroundLips(
                            resized, landmarks[i].landmark)

                    

            # Put the frame with the needed ROI in queue
            self.face1Queue.put(croppedLipsFrame1)
            self.face2Queue.put(croppedLipsFrame2)

            # print("show frame")
            # cv2.imshow("frame", frame)
            # cv2.imshow('faceMeshDetectionFrame', faceMeshDetectionFrame)

            cv2.imshow('drawRectAroundLipsFrame1', rectAroundLipsFrame1)
            cv2.imshow('drawRectAroundLipsFrame2', rectAroundLipsFrame2)
            
            cv2.imshow('croppedFrame1', croppedLipsFrame1)

            cv2.imshow('croppedFrame2', croppedLipsFrame2)


            # need to be in a variable because else it will not work immediately
            pressedKey = cv2.waitKey(1)
            if pressedKey == ord('q'):
                break
            elif pressedKey == ord("c"):
                print("Change Camera to face " + str(self.detectFace0))
                self.detectFace0 = 0 if self.detectFace0 == 1 else 1

        cap.release()
        cv2.destroyAllWindows()

    def faceMeshDetection(self, frame):
        """
        Detects the face and the landmarks of the face with mediapipe
        and draws only the landmarks on the frame to the face we want. 
        Also puts the face number 

        Args:
            frame (numpy.ndarray): The frame we want to detect the face and the landmarks on.

        Returns:
            numpy.ndarray: The frame with the landmarks on the face we want.
        """
        faceMeshFrame = frame.copy()

        height = faceMeshFrame.shape[0]
        width = faceMeshFrame.shape[1]

        # create RGB frame because mediapipe use RGB
        frameRGB = cv2.cvtColor(faceMeshFrame, cv2.COLOR_BGR2RGB)

        # FaceMesh with 468 points
        self.faceMeshResult = self.faceMesh.process(frameRGB)
        if self.faceMeshResult.multi_face_landmarks:
            for i in range(0, len(self.faceMeshResult.multi_face_landmarks)):
                if self.faceMeshResult.multi_face_landmarks[i]:


                    # Puts face number
                    cv2.putText(faceMeshFrame, "Face " + str(i), (int(self.faceMeshResult.multi_face_landmarks[i].landmark[0].x * width - 50), int(
                        self.faceMeshResult.multi_face_landmarks[i].landmark[0].y * height - 50)), FONT, 1, (0, 0, 255), 1)

                    self.mpDraw.draw_landmarks(faceMeshFrame, self.faceMeshResult.multi_face_landmarks[i],
                                                   self.mpFaceMesh.FACEMESH_CONTOURS,
                                                   connection_drawing_spec=self.landmarkConnectionSpecs,
                                                   landmark_drawing_spec=self.landmarkDrawingSpecs)

            return faceMeshFrame, self.faceMeshResult.multi_face_landmarks

        return None, None
        # noFaceDetected = np.zeros((height, width, 3), np.uint8)
        # cv2.putText(noFaceDetected, "No face detected", (int(
        #     width // 2 - 100), int(height // 2)), FONT, 1, (0, 0, 255), 1)
        # return noFaceDetected, None

    def drawRectAroundLips(self, frame, landmarks):
        """Draws a rectangle around the lips and 
            and calls the function [cropLips] to crop the lips
            and show it in a new window

        Args:
            frame (numpy.ndarray): The frame we want to draw the rectangle on.
            landmarks (list): The landmarks of the face we want to draw the rectangle on.

        Returns:
            numpy.ndarray: The frame with the rectangle around the lips.
        """

        rectAroundLipsFrame = frame.copy()

        width = rectAroundLipsFrame.shape[1]
        height = rectAroundLipsFrame.shape[0]

        if(landmarks is not None):

            minX = width
            maxX = 0
            minY = height
            maxY = 0

            minXWithGap = 0
            maxXWithGap = 0
            minYWithGap = 0
            maxYWithGap = 0

            # Get all the landmarks of the lips
            FACEMESH_LIPS_TUPLE = list(self.mpFaceMesh.FACEMESH_LIPS)
            FACEMESH_LIPS_LIST = []
            for pointdrawRectAroundLips in FACEMESH_LIPS_TUPLE:
                FACEMESH_LIPS_LIST.append(pointdrawRectAroundLips[0])
                FACEMESH_LIPS_LIST.append(pointdrawRectAroundLips[1])

            # Go through all the landmarks of the lips and get the min and max values
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

            cv2.rectangle(rectAroundLipsFrame, (minXWithGap, minYWithGap),
                          (maxXWithGap, maxYWithGap), (255, 0, 0), 2)

            cropedLips = self.cropLips(
                rectAroundLipsFrame, minXWithGap, maxXWithGap, minYWithGap, maxYWithGap)

            return rectAroundLipsFrame, cropedLips
        else:
            noFaceDetected = np.zeros((height, width, 3), np.uint8)
            cv2.putText(noFaceDetected, "No face detected", (int(
                width // 2 - 100), int(height // 2)), FONT, 1, (0, 0, 255), 1)
            return noFaceDetected, None

    def cropLips(self, frame, minX, maxX, minY, maxY):
        """Crops the lips from the frame and shows it in a new window

        Args:
            frame (numpy.ndarray): The frame we want to crop the lips from.
            minX (int): The minimum x value of the lips.
            maxX (int): The maximum x value of the lips.
            minY (int): The minimum y value of the lips.
            maxY (int): The maximum y value of the lips.

        Returns:
            numpy.ndarray: The frame with the cropped lips.
        """
        cropedLips = frame.copy()

        # TODO: Look up how VisualVoice does the cropping
        cropedLips = cropedLips[minY:maxY, minX:maxX]
        resizedLips = cv2.resize(
            cropedLips, (ROI_FRAME_HEIGHT, ROI_FRAME_WIDHT), interpolation=cv2.INTER_NEAREST)

        # print("Croped Lips:" + str(cropedLips.shape))

        # Croped Lips:(71, 76, 3)
        # Croped Lips:(72, 75, 3)
        # Croped Lips:(70, 76, 3)
        # Croped Lips:(67, 73, 3)
        # Croped Lips:(60, 68, 3)
        # Croped Lips:(52, 64, 3)
        # Croped Lips:(52, 64, 3)

        # original
        # Mouth shape: (208, 96, 96)

        return resizedLips
