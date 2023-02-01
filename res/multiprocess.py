# from capVideoMultiprocessing import capVideoFunc
from multiprocessing import Process, Queue, Array
import cv2
from jackClient_acssMultiprocessing import AudioCapture
from syncLoop import SyncLoop
from videoCapture import CaptureVideo
import jack
import numpy
# from dnnModellCall import DnnModelCall
# from audioCapture import AudioCaptureNew
import jack
import threading
from multiprocessing import Process, Queue
import numpy as np
import librosa
from helperFunctions import *
import global_variables as gv
from scipy import signal



client = jack.Client("AVSS")

event = threading.Event()


audioBufferInQueue = Queue()
dnnOutQueue = Queue()
audioBufferOut = [0] * gv.AUDIO_BUFFER_OUT_SIZE


class AudioCaptureNew(Process):
    
    def __init__(self):
        super().__init__()
        print("AudioCapture: init")
        
        # global testQueue
        # testQueue = audioBufferInQueue
        
    def run(self):
        global soundFile
        global soundPos
        global spkGainAbs
        global playActive
        
        print("AudioCapture: run")
        
        if client.status.server_started:
            print("JACK server started")
        if client.status.name_not_unique:
            print("unique name {0!r} assigned".format(client.name))


        samplerate = 48000
        audioPath = r'resources\misc\gerkmannFrintrop.wav' # "/export/scratch/studio/StudioScripts/Demos/SpeechEnhancementAndSeparation/AudioInput/48k/Speech_Female01.wav" 

        # Changing to 32000 for the current settings
        soundFile = []
        TMP_samplerate = 32000
        sample_48k = librosa.load(audioPath, sr=samplerate)[0]
        sample = librosa.resample(sample_48k, orig_sr=samplerate, target_sr=TMP_samplerate)
        # print(f'{sample.shape=}')
        soundFile.append(sample)

        soundPos = np.zeros(1, dtype="int32")
        playActive = np.ones(1, dtype=bool)
        spkGainAbs = np.ones(1)


        # create port for the input speech ("mixed_speech") and the both speaker
        client.inports.register("mixed_speech")
        client.outports.register("speaker1")
        client.outports.register("virtualSource")
        
        with client:
            print("AudioCapture: run")
            
            capture = client.get_ports(is_physical=True, is_output=True)
            if not capture:
                raise RuntimeError("No physical capture ports")

            for src, dest in zip(capture, client.inports):
                client.connect(src, dest)

            playback = client.get_ports(is_physical=True, is_input=True)
            if not playback:
                raise RuntimeError("No physical playback ports")

            for src, dest in zip(client.outports, playback):
                client.connect(src, dest)

            print("Press Ctrl+C to stop")
            try:
                event.wait()
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                
                
    @client.set_process_callback
    def process(frame):
        assert frame == client.blocksize
        
        global audioBufferOut
        
        # play virtualSources on the right speaker (headset)
        virtualSource = virtaulSources(soundFile, soundPos, client,  playActive, spkGainAbs)
        client.outports[1].get_array()[:] = virtualSource
        
        # get the input of the mic
        audioFrameCurrent32kHz = client.inports[0].get_array()[:]

        # Downsample from 32 kHz to 16 kHz samplerate
        # ATTENTION: Signal must be prefiltered with low pass at Nyquist (< 4 kHz)
        audioFrameCurrent32kHz, gv.FILTER_STATES_LP_DOWN_SAMPLE = signal.lfilter(gv.b, gv.a, audioFrameCurrent32kHz, zi=gv.FILTER_STATES_LP_DOWN_SAMPLE)
        audioFrameCurrent16kHz = audioFrameCurrent32kHz[::gv.DOWN_SAMPLING_FACTOR]

        
        # get the new audioFrame at 16kHz
        newAudioFrame = audioFrameCurrent16kHz
        # print("newAudioFrame length: \t" + str(len(newAudioFrame)))
        
        print("PUT")
        audioBufferInQueue.put(newAudioFrame)
        
        if(not dnnOutQueue.empty()):
            print("not empty")
            dnnModelResult = dnnOutQueue.get()
            audioBufferOut.extend(dnnModelResult)
            # print("audioBufferOut after extend length: \t" + str(len(gv.audioBufferOut)))

        # print("audioBufferOut length: \t" + str(len(audioBufferOut)))
        # get the first 128 samples
        outputForUpsampling = audioBufferOut[:128]
        # print("outputForUpsampling length: \t" + str(len(outputForUpsampling)))

        # remove the first 128 samples
        audioBufferOut = audioBufferOut[128:]

        # Upsample from 8 kHz 48 kHz
        dataCurrentOut32kHz = np.zeros_like(audioFrameCurrent32kHz)
        # print("data: " + str(dataCurrentOut32kHz.shape))
        dataCurrentOut32kHz[::gv.DOWN_SAMPLING_FACTOR] = outputForUpsampling # outputForUpsampling # newAudioFrame
        dataCurrentOut32kHz, gv.FILTER_STATES_LP_UP_SAMPLE_CHANNEL0 = signal.lfilter(gv.DOWN_SAMPLING_FACTOR*gv.b, gv.a, dataCurrentOut32kHz, zi=gv.FILTER_STATES_LP_UP_SAMPLE_CHANNEL0)


        # output
        client.outports[0].get_array()[:] = dataCurrentOut32kHz # audioFrameCurrent32kHz # client.inports[0].get_array() # dataCurrentOut32kHz # client.inports[0].get_array() # dataCurrentOut32kHz
        
    
    @client.set_shutdown_callback
    def shutdown(status, reason):
        print("JACK shutdown!")
        print("status:", status)
        print("reason:", reason)


        event.set()
        

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
            if(not audioBufferInQueue.empty()):
                # gv.trigger.get()
                print("TRIGGER")
                k = 0
                audioBufferIn = audioBufferInQueue.get() # [0] * 3000 # 
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
                dnnOutQueue.put(outputDnnHintererTeil)
                # print("Calculation done")

            # if 40800
                


if __name__ == '__main__':
    """
    Wir haben nur eine VideoQueue, da wir nur die frames rübergeben wollen
    zu audioCapture
    im audioCapture wird dann eine audioBuffer erstellt und ein videoBuffer
    das was wir besprochen haben
    und dann werden die buffers an den DnnModelCall übergeben
    """

    # initilize queue to share data between processes on frame per 0.04 s

    # init audioFrameQueue
    # audioBufferInQueue = Queue()
    # fill the audioBufferInQueue with 0
    # audioBufferInQueue.put([0] * 40800)  # numpy geht nicht weil zu groß

    
    # testGlobal = GlobalTestClass(audioBufferInQueue)


    # dnnOutQueue for continous output
    # dnnModelCall = DnnModelCall(
    #     dnnOutQueue, videoFrameQueue, audioBufferInQueue, trigger)
    dnnModelCall = DnnModelCall()
    dnnModelCall.start()


    # # add VideoCaputure as process
    # captureVideo = CaptureVideo(videoFrameQueue, 0)
    # captureVideo.start()



    # add AudioCaputure as process
    audioCapture = AudioCaptureNew() # AudioCapture(audioBufferInQueue, videoFrameQueue, dnnOutQueue)
    audioCapture.start()
    
    #! Wait for them to finish which will never happen because it is a True loop
    dnnModelCall.join()
    # captureVideo.join()
    audioCapture.join()