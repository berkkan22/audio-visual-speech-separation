import multiprocessing

from face_detection_def import testDetection
from face_mesh_def import testMesh
import cv2



def loop1(a):
  while True:
    print(a)
    print("Loop1")

def loop2(b):
  while True:
    print(b)
    print("Loop2")
    
    
def main():
  print("Start")
  # manager = multiprocessing.Manager()
  # pool = multiprocessing.Pool()
  
  # cam = manager.Queue()
  
  cap = cv2.VideoCapture(0)
  
  # cam.put(cap)


  # pool.apply_async(testMesh, ())
  # pool.apply_async(testDetection, ())

  # pool.close()
  # pool.join()
  
  p1 = multiprocessing.Process(target = testMesh, args=(cap,))
  p2 = multiprocessing.Process(target = testDetection, args=(cap,))
  p1.start()
  p2.start()
  p1.join()
  p2.join()

if __name__ == "__main__":
    main()