import cv2


def capVideoFunc(cap):
    # for i in range(2):
    ref, frame = cap.read()
    # cv2.imshow("Frame Raw", frame)
    if cv2.waitKey(1) == ord("q"):
        return
    return frame