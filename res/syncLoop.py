from multiprocessing import Process

class SyncLoop(Process):
  def __init__(self, videoqueue, audioQueue):
    super().__init__()
    self.videoqueue = videoqueue
    self.audioQueue = audioQueue
    
    
  def run(self):
    audioBuffer = [] # audioBuffer contains 5 elements
    bo = True # Test var to print output only once

    while True:
      # print("testLoopSize: " + str(self.videoqueue.qsize()))
      # videoFrame = self.videoqueue.get()
      # print("TestLoop Frame: " + str(videoFrame))
      # print("Test Loop: " + str(self.audioQueue.get()))


      if(len(audioBuffer) < 5):
        print("Start")
        audioBuffer.append(self.audioQueue.get())
      else:
        # TODO: sync here
        if(bo):
          print("Start sync")
          print(audioBuffer)
          size = self.videoqueue.qsize()
          print(self.videoqueue.get())
          print(len(audioBuffer))
          print(size)
          bo = False

          # arent them already sync?
          # call ML model?
          # ....


        # remove everything
        audioBuffer = []
