import sys
import os
import cv2

# Garante que consiga importar a biblioteca estando dentro da subpasta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kinect_lib import KinectSensor

def main():
    print("=== Exemplo 4: Controle do Motor de Inclinação ===")
    kinect = KinectSensor()
    
    # Liga apenas a câmera RGB para termos feedback visual
    if kinect.start(enable_color=True):
        print("Use as teclas 'w' (subir) e 's' (descer). Pressione 'q' para sair.")
        try:
            while True:
                frame = kinect.get_color_frame()
                if frame is not None:
                    cv2.imshow("Controle Motor do Kinect", frame)
                    
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('w'):
                    atual = kinect.get_tilt()
                    # A biblioteca protege o valor limite automaticamente pra não quebrar.
                    kinect.set_tilt(atual + 5)
                    print(f"Subindo... Inclinação atual: {kinect.get_tilt()}°")
                    
                elif key == ord('s'):
                    atual = kinect.get_tilt()
                    kinect.set_tilt(atual - 5)
                    print(f"Descendo... Inclinação atual: {kinect.get_tilt()}°")
                    
                elif key == ord('q'):
                    break
        finally:
            kinect.stop()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
