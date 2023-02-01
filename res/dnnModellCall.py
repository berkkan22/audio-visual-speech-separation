from multiprocessing import Process
import time
import global_variables as gv
import audioCapture as ac


class DnnModelCall(Process):
    # def __init__(self, queue, videoBuffer, audioBuffer, triggerQueue):
    def __init__(self):
        super().__init__()
        print("DnnModelCall: init")
        # self.queue = queue
        # self.videoBuffer = videoBuffer
        # self.audioBuffer = audioBuffer
        # self.triggerQueue = triggerQueue

    def run(self):
        print("DnnModelCall: run")
        while True:
            # print("RUNNNNN")
            # print(len(ac.testBufferOut))
            if(not ac.testBufferIn.empty()):
                # gv.trigger.get()
                k = 0
                audioBufferIn = gv.audioBufferInQueue.get() # [0] * 3000 # 
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
                print(audioBufferIn.shape)
                outputDnnHintererTeil = audioBufferIn
                gv.dnnOutQueue.put(outputDnnHintererTeil)
                # print("Calculation done")

            # if 40800
                