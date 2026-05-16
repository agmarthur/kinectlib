import sys
import os
import cv2

# Garante que consiga importar a biblioteca estando dentro da subpasta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kinect_lib import KinectSensor

def main():
    print("=== Exemplo 1: Câmera RGB Padrão ===")
    kinect = KinectSensor()
    
    # Liga apenas a câmera colorida
    if kinect.start(enable_color=True):
        print("Pressione 'q' na janela de vídeo para sair.")
        try:
            while True:
                frame = kinect.get_color_frame()
                if frame is not None:
                    cv2.imshow("Kinect RGB (Cores)", frame)
                    
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            kinect.stop()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
