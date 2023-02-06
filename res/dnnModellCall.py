from torch.multiprocessing import *
import time
from helperFunctions import *
from global_variables import *

import sys
sys.path.append("./visualvoice")
# from testcall import init
from visualvoice_demo import buildModel, runModel


class DnnModelCall(Process):
    def __init__(self, audioBufferInQueueParam, audioBufferDNNOutParam):
        super().__init__()
        print("DnnModelCall: init")

        set_start_method("spawn", force=True)

        
        self.audioBufferInQueueParam = audioBufferInQueueParam
        self.audioBufferDNNOutParam = audioBufferDNNOutParam

        self.model, self.opt = buildModel()


    def run(self):
        print("DnnModelCall: run")
        localBuffer = [0] * 40800
        # localBuffer = []
        count = 0
        while True:
            if(not self.audioBufferInQueueParam.empty()):

                # while(not self.audioBufferInQueueParam.empty() and len(localBuffer) <= 40800):
                while(not self.audioBufferInQueueParam.empty() and count < COUNT):
                    localBuffer = removeFirstFrameAndAddNewFrame(localBuffer, self.audioBufferInQueueParam.get())
                    # localBuffer.extend(self.audioBufferInQueueParam.get())
                    # print(f"localBuffer: {len(localBuffer)}")
                    count += 1

            # if(len(localBuffer) >= 40800):
            if(count >= COUNT):
                # print("Start")
                audioBuffer = localBuffer
                # print(len(localBuffer))
                # print(len(audioBuffer[-2560::]))
                # time.sleep(0.1) # laufzeit von DNN
                # try:
                # speaker1, speaker2 = runModel(self.model, self.opt)
                # except:
                    # time.sleep(0.1)
                # finally:

                self.audioBufferDNNOutParam.put(audioBuffer[(DNN_AUDIO_FRAME_SIZE*-COUNT)::])
                # localBuffer = []
                count = 0
                