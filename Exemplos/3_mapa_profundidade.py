import sys
import os
import cv2
import numpy as np

# Garante que consiga importar a biblioteca estando dentro da subpasta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kinect_lib import KinectSensor

def main():
    print("=== Exemplo 3: Mapa de Profundidade em Cores ===")
    kinect = KinectSensor()
    
    # Liga o Color e o Depth (Profundidade pode rodar com Color ou com IR)
    if kinect.start(enable_color=True, enable_depth=True):
        print("Pressione 'q' na janela de vídeo para sair.")
        try:
            while True:
                frame_rgb = kinect.get_color_frame()
                frame_depth = kinect.get_depth_frame()
                
                # Exibe a câmera colorida se houver
                if frame_rgb is not None:
                    cv2.imshow("Kinect RGB Original", frame_rgb)
                    
                # Exibe a profundidade (Vem em 16-bits / Milímetros)
                if frame_depth is not None:
                    # Mapeia as distâncias pra 8-bits pra exibir direito (divide por 32).
                    # Depois aplica um mapa de calor pra dar o efeito visual legal (JET).
                    depth_8u = (frame_depth / 32).astype(np.uint8) 
                    depth_colorida = cv2.applyColorMap(depth_8u, cv2.COLORMAP_JET)
                    
                    cv2.imshow("Kinect Mapa Profundidade 3D", depth_colorida)
                    
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            kinect.stop()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
