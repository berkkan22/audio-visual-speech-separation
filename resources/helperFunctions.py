from global_variables import AUDIO_FRAME_SIZE, DOWN_SAMPLING_FACTOR


def removeFirstAudioFrameAndAddNewAudioFrame(audioBuffer, newAudioFrame):
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

def removeFirstVideoFrameAndAddNewVideoFrame(videoBuffer, newvideoFrame):
    """
        Removes the first frame of the [videoBuffer] and 
        adds the new frame [newvideoFrame] to the [videoBuffer]
        and returns it 

        Args:
            videoBuffer (list?array): The video buffer with the frames
            newvideoFrame (numpy.ndarray): The new video frame which will be added to the video buffer

        Return:
            numpy.ndarray: [videoBuffer] with the new frame at the end

    """

    videoBuffer = videoBuffer[1:]
    videoBuffer.append(newvideoFrame)

    return videoBuffer

def virtaulSources(soundFile, soundPos, client, spkGainAbs, playActive):
    if soundPos[0]+client.blocksize > soundFile[0].size:
        soundPos[0] = 0
    virtaulSource = soundFile[0][soundPos[0]:soundPos[0]+client.blocksize] * 0.1 #* spkGainAbs[0] * playActive[0]
    # print(f'{len(audioFrameCurrent32kHz)}')
    soundPos[0] += client.blocksize #* playActive[0]
    
    return virtaulSource