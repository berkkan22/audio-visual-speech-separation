from global_variables import AUDIO_FRAME_SIZE, DOWN_SAMPLING_FACTOR


def removeFirstFrameAndAddNewFrame(audioBuffer, newAudioFrame):
    """
        Removes the first frame of the [audioBuffer] and 
        adds the new frame [newAudioFrame] to the [audioBuffer]
        and returns it 

        Args:
            audioBuffer (list?array): The audio buffer with the audio
            newAudioFrame (numpy.ndarray): The new a udio frame which will be added to the audio buffer

        Return:
            numpy.ndarray: [audioBuffer] with the new frame at the end

    """

    # remove first 128 element
    audioBuffer = audioBuffer[int(AUDIO_FRAME_SIZE/DOWN_SAMPLING_FACTOR):]
    # add new audio frame to buffer
    audioBuffer.extend(newAudioFrame)

    return audioBuffer

def virtaulSources(soundFile, soundPos, client, spkGainAbs, playActive):
    """
        Creates the virtual sources loop

        Args:
            soundFile (list): the sound sample. Each file is a new element in the list
            soundPos (list<int>): is the position of the current sound file
            client (Client): the jack client to get the blocksize
            spkGainAbs:
            playActive:
    """
    
    VOLUME = 0.1

    if soundPos[0]+client.blocksize > soundFile[0].size:
        soundPos[0] = 0
    virtaulSource = soundFile[0][soundPos[0]:soundPos[0]+client.blocksize] * VOLUME #* spkGainAbs[0] * playActive[0]
    # print(f'{len(audioFrameCurrent32kHz)}')
    soundPos[0] += client.blocksize #* playActive[0]
    
    return virtaulSource