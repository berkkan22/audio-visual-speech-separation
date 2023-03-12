# AudioVisualSpeechSeparation

[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)

This is the repository of my bachelor thesis. Here I will write all the code. This includes the video preprocessing with different face-tracking models, audio preprocessing and also the synchronization of the audio and video. Additionally, if time is left, I will create a UI as well. <br>
The title of my bachelor thesis is **"Robust preprocessing for real-time audio-visual speech separation"**. Audio-visual speech separation is a multi-modal method. This approach uses the audio and video information to separate the speakers. [[1]](#1) <br>
The goal of this thesis is to create a real-time preprocessing module for audio-visual speech separation. The focus is on preprocessing, which is marked in orange in the image below.

[![Audio-visual speech separation structure](/images/problem_description_full.png)](LINK)
_Audio-visual speech separation structure_

---

## Project struckture

```
.
├── README.md
├── checkpoints                                 # output txt of visualVoice
├── images
├── requirements.txt                            # required libarys
├── resources
│   ├── audioCapture.py                         # process for the audio preprocessing
│   ├── buffer test.py
│   ├── captureVideo                            # video caputre tests
│   ├── code                                    # basic jack client script
│   ├── dnnModellCall.py                        # procces for the DNN call
│   ├── global_test.py
│   ├── global_variables.py                     # global variables
│   ├── helperFunctions.py                      # helperfunctions
│   ├── jackClient_acssMultiprocessing.py
│   ├── misc
│   ├── multiprocess.py                         # initilize the process and queues and start them
│   ├── patchbay files                          # patchbay files for the jack client
│   ├── test.py
│   ├── video540p.mp4
│   └── videoCapture.py                         # process for the video preprocessing
└── visualvoice                                 # visualVoice DNN model code
```

## Getting started

A quick introduction to installing everything you need and running the code.

### Requirements

I'm using **python 3.9** to run this code, so I recommend installing it too. If you do not have python you can check [this installation guide](https://realpython.com/installing-python/)

### Creating a virtual python environment

Before you install all libraries I recommend to first creating a virtual environment tp prevent version conflicts. <br>
To create a virtual environment type `python -m venv ./venv ` in the command line.

<!-- Asciinema to recorde comand line -->

### Install libraries

Now you have created virtual environment you need to go into that environment. <br>
On **windows** type this `call ./venv/Scripts/activate.bat` to activate and this `deactivate.bat` to deactivate. <br>
On **linux** type this `source ./venv/Scripts/activate` to activate and this `deactivate.bat` to deactivate. <br>
If you are in the virtaul environment you should see `(venv)` in front of your command line. <br>
Now you can install all the libraries. Type `pip install -r requirements.txt` to install all the libraries. <br>

## Running the code

To run the code you need to start the jack server. After that you can start the code by typing `python ./resources/multiprocess.py` in the command line. <br>

## Known issues

Sometimes the process can not share there queues. This is a known issue and I'm working on it. But if you start `multoprocess.py` again at some point it works. <br>

## Support

If you have trouble with the installation or with running the code or have any other questions feel free to contact me.
You can reach me throw GitLab @9katirci or via email at berkkan.katirci@studium.uni-hamburg.de or berkkan22@gmail.com

## References

<a id="1">[1]</a>
Daniel Michelsanti, Zheng-Hua Tan, Shi-Xiong Zhang, Yong Xu, Meng
Yu, Dong Yu, and Jesper Jensen. _An overview of deep-learning-based
audio-visual speech enhancement and separation_. IEEE ACM Trans.
Audio Speech Lang. Process., 29:1368–1396, 2021.
