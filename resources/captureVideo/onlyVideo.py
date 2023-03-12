import cv2
import acapture

cap = cv2.VideoCapture(0)
# cap = acapture.open(0)


while True:
    ref, frame = cap.read()
    # print(frame)
    # frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    try:
        cv2.imshow("Frame Raw", frame)
    except:
        print("ERROR")

    if cv2.waitKey(1) == ord("q"):
        break

# Stop cv2
cap.release()
cv2.destroyAllWindows()