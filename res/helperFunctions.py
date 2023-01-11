from global_variables import AUDIO_FRAME_SIZE, DOWN_SAMPLING_FACTOR


def removeFirstFrameAndAddNewFrame(audioBuffer, newAudioFrame):
    """
        Removes the first frame of the [audioBuffer] and 
        adds the new frame [newAudioFrame] to the [audioBuffer]
        and returns it 

        Args:
            audioBuffer (numpy.ndarray): The audio buffer with the audio
            newAudioFrame (numpy.ndarray): The new a udio frame which will be added to the audio buffer

        Return:
            numpy.ndarray: [audioBuffer] with the new frame at the end

    """
    # remove first 128 element
    audioBuffer = audioBuffer[int(AUDIO_FRAME_SIZE/DOWN_SAMPLING_FACTOR):]
    # add new audio frame to buffer
    audioBuffer.extend(newAudioFrame)

    return audioBuffer



# add under the function
# remove first 128 element
# audioBufferInputModified = audioBufferInput[int(AUDIO_FRAME_SIZE/DOWN_SAMPLING_FACTOR):]
# # add new audio frame to buffer
# audioBufferInputModified.extend(newAudioFrame)

# put it again in the queue so it can be used in the DNN process
# audioBufferInQueue.put(newAudioBuffer)