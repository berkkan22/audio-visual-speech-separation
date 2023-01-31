from multiprocessing import Process
import time


class DnnModelCall(Process):
    def __init__(self, queue, videoBuffer, audioBuffer, triggerQueue):
        super().__init__()
        print("DnnModelCall: init")
        self.queue = queue
        self.videoBuffer = videoBuffer
        self.audioBuffer = audioBuffer
        self.triggerQueue = triggerQueue

    def run(self):
        print("DnnModelCall: run")
        while True:
            if(not self.audioBuffer.empty()):
                self.triggerQueue.get()
                k = 0
                audioBufferIn = self.audioBuffer.get() # [0] * 3000 # 
                # audioBufferIn = self.audioBuffer.get()
                # self.audioBuffer.put(audioBufferIn, block=False)
                # print("\n**************************************************")
                # print("********** Start DNN Model Process here **********")
                # print("**************************************************\n")
                # for i in range(0, 1000): 
                #     k += 1
                    # TODO: Call DNN Model here
                    # outputDnn = audioBufferIn
                    # add new audio frame to buffer
                outputDnnHintererTeil = audioBufferIn[-2560:]
                self.queue.put(outputDnnHintererTeil)
                # print("Calculation done")

            # if 40800
                