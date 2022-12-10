import cv2

cap = cv2.VideoCapture(0)

while True:
    ref, frame = cap.read()
    print(frame)

    try:
        cv2.imshow("Frame Raw", frame)
    except:
        print("ERROR")

    if cv2.waitKey(1) == ord("q"):
        break

    # Stop cv2
    cap.release()
    cv2.destroyAllWindows()