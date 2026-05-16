import sys
import os
import cv2
import numpy as np

# Garante que consiga importar a biblioteca estando dentro da subpasta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kinect_lib import KinectSensor

def main():
    print("=== Exemplo 2: Câmera Infravermelha (IR) ===")
    kinect = KinectSensor()
    
    # O IR não pode rodar junto com a cor normal. Liga apenas o IR.
    if kinect.start(enable_color=False, enable_ir=True):
        print("Pressione 'q' na janela de vídeo para sair.")
        try:
            while True:
                frame_ir = kinect.get_color_frame()
                if frame_ir is not None:
                    # O sensor IR envia 16-bits. O OpenCV desenha bem usando 8-bits.
                    # Vamos ignorar os 8 bits de baixo usando shift-right (>> 8).
                    frame_8u = (frame_ir >> 8).astype(np.uint8)
                    cv2.imshow("Kinect IR (Visao Noturna)", frame_8u)
                    
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            kinect.stop()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
