from multiprocessing import Process
import cv2

FPS = 25

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
        self.queue.put(frame)

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
    
