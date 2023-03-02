from multiprocessing import *
import time
from helperFunctions import *
from global_variables import *

import sys
sys.path.append("./visualvoice")
# from testcall import init
from visualvoice_demo import buildModel, runModel


class DnnModelCall(Process):
    def __init__(self, audioBufferInQueueParam, audioBufferDNNOutParam, face1Queue, face2Queue):
        super().__init__()
        print("DnnModelCall: init")

        
        self.audioBufferInQueueParam = audioBufferInQueueParam
        self.audioBufferDNNOutParam = audioBufferDNNOutParam

        self.face1Queue = face1Queue
        self.face2Queue = face2Queue

        self.model, self.opt = buildModel()


    def run(self):
        print("DnnModelCall: run")
        localBuffer = [0] * 40800
        face1Buffer = [np.zeros((ROI_FRAME_HEIGHT, ROI_FRAME_WIDHT, ROI_FRAME_CHANNELS), dtype=np.uint8)] * 64
        face2Buffer = [np.zeros((ROI_FRAME_HEIGHT, ROI_FRAME_WIDHT, ROI_FRAME_CHANNELS), dtype=np.uint8)] * 64

        countAudioSamples = 0
        countVideoFrames = 5

        while True:
            if(not self.audioBufferInQueueParam.empty() and not self.face1Queue.empty() and not self.face2Queue.empty()):

                # while(not self.audioBufferInQueueParam.empty() and len(localBuffer) <= 40800):
                while(not self.audioBufferInQueueParam.empty() and countAudioSamples < COUNT):
                    localBuffer = removeFirstAudioFrameAndAddNewAudioFrame(localBuffer, self.audioBufferInQueueParam.get())
                    if(countVideoFrames == 5 and not self.face1Queue.empty() and not self.face2Queue.empty()):
                        face1Buffer = removeFirstVideoFrameAndAddNewVideoFrame(face1Buffer, self.face1Queue.get())
                        face2Buffer = removeFirstVideoFrameAndAddNewVideoFrame(face2Buffer, self.face2Queue.get())

                        countVideoFrames = 0

                    # localBuffer.extend(self.audioBufferInQueueParam.get())
                    # print(f"localBuffer: {len(localBuffer)}")
                    countAudioSamples += 1
                    countVideoFrames += 1
                

            # if(len(localBuffer) >= 40800):
            if(countAudioSamples >= COUNT):
                # print("Start")
                audioBuffer = localBuffer
                # print(len(localBuffer))
                # print(len(audioBuffer[-2560::]))
                # time.sleep(0.1) # laufzeit von DNN
                # try:
                # print("runModel")
                start = time.time()
                speaker1, speaker2 = runModel(self.model, self.opt, audioInput=audioBuffer)
                end = time.time()
                print(f"Laufzeit DNN: {end-start}")
                # print(speaker1)
                # print(speaker2)
                # except:
                    # time.sleep(0.1)
                # finally:

                self.audioBufferDNNOutParam.put(speaker2[(DNN_AUDIO_FRAME_SIZE*-COUNT)::])
                # localBuffer = []
                countAudioSamples = 0
                