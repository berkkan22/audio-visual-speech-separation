import cv2

from setup_mediapipe import faceTrackLoop


continueProcess = True

# Take webcam as camera
cap = cv2.VideoCapture(0)

while continueProcess:
  option = int(input("What program should run? "))
  
  if option == 1:
    # exit
    print("EXIT")
  elif option == 2:
    # loop:
    faceTrackLoop(cap, option)
    print("ALL")
  else:
    print("Wrong number")
