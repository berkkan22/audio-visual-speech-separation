import cv2


def capVideoFunc(cap, frameList):
    # for i in range(2):
    ref, frame = cap.read()
    # cv2.imshow("Frame Raw", frame)
    frameList.append(frame)
    
    if cv2.waitKey(1) == ord("q"):
        return