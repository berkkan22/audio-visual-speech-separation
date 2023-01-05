from multiprocessing import Process
import time


class DnnModelCall(Process):
    def __init__(self, queue, videoBuffer, audioBuffer):
        super().__init__()
        print("DnnModelCall: init")
        self.queue = queue
        self.videoBuffer = videoBuffer
        self.audioBuffer = audioBuffer

    def run(self):
        print("DnnModelCall: run")
        while True:
            if(not self.audioBuffer.empty()):
                # getedAudioBuffer = self.audioBuffer.get()
                k = 0
                print("\n**************************************************")
                print("********** Start DNN Model Process here **********")
                print("**************************************************\n")
                audioBufferIn = self.audioBuffer.get()
                for i in range(0, 100000000): # ca. 9 sekunden
                    k += 1
                    # TODO: Call DNN Model here
                    outputDnn = audioBufferIn
                    # add new audio frame to buffer
                outputDnnHintererTeil = outputDnn[-2560:]
                outputQueue = self.queue.get()
                outputQueue.extend(outputDnnHintererTeil)
                self.queue.put(outputQueue)
                print("Calculation done")
