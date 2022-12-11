from multiprocessing import Process
import cv2
import numpy as np

FPS = 25
VIDEO_BUFFER_SIZE = 64

# or make it as a flatted shape?
videoBufferFromThePast = np.zeros(VIDEO_BUFFER_SIZE)


class CaptureVideo(Process):
  def __init__(self, queue, streamID):
  # def __init__(self, streamID):
    super().__init__()
    self.queue = queue
    self.streamID = streamID
    
  def run(self):
    print("Started video capture process")
    cap = cv2.VideoCapture(self.streamID)
    cap.set(cv2.CAP_PROP_FPS, FPS) # set FPS to 25 to sync it good with the audio_buffer
    
    if(cap.isOpened()):
      print("Started video capture")
      while True:
        ref, frame = cap.read()

        # the queue will always be empty because in the sync Process there we get the element
        
        # ein element im buffer ist ein frame
        videoBufferFromThePast[VIDEO_BUFFER_SIZE-1::] = frame
        temp = videoBufferFromThePast[1::]
        videoBufferFromThePast = np.append(temp, np.zeros(1))
        print(videoBufferFromThePast)
        self.queue.put(videoBufferFromThePast)
        

        cv2.imshow("Frame", frame)
        
        # TODO: call video preprocessing function

        if cv2.waitKey(1) == ord("q"):
          break
    
    print("Capture device is could not be open")


  def getFrame(self):
    return self.queue

  def faceMeshDetection(frame):
    pass

  def faceDetection(frame):
    pass

  def croppLips(frame):
    pass
    
