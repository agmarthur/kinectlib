import clr
import os
import sys
import numpy as np
import cv2
import time
import logging

# Configuração de log profissional (padrão de mercado)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("KinectLib")

class KinectSensor:
    """
    Biblioteca de interface com o Kinect v1 via DLL C#.
    Requer: Microsoft Kinect SDK v1.8 instalado no Windows.
    """
    def __init__(self, dll_path: str = None):
        if dll_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            dll_path = os.path.join(script_dir, "bin", "Debug", "net48", "KinectInterop.dll")
        
        if not os.path.exists(dll_path):
            logger.error(f"DLL não encontrada: {dll_path}")
            logger.error("Certifique-se de compilar o projeto C# (dotnet build) antes de executar.")
            raise FileNotFoundError(f"DLL C# não encontrada em: {dll_path}")
            
        try:
            clr.AddReference(dll_path)
            from KinectInterop import KinectCapture
            self._capture = KinectCapture()
        except Exception as e:
            logger.error("Falha ao carregar a DLL. O Microsoft Kinect SDK v1.8 está instalado neste PC?")
            raise RuntimeError(f"Erro Crítico de Inicialização do Kinect: {e}")

    def start(self, enable_color: bool = True, enable_depth: bool = False, enable_ir: bool = False) -> bool:
        """
        Inicializa o sensor Kinect.
        Nota: Color e IR usam o mesmo fluxo e não podem estar ativos simultaneamente.
        """
        if enable_color and enable_ir:
            logger.warning("Color e IR foram solicitados juntos. O hardware não suporta. Priorizando IR.")
            enable_color = False
            
        self.is_ir = enable_ir
        logger.info(f"Iniciando sensor. Modos -> RGB: {enable_color} | Depth: {enable_depth} | IR: {enable_ir}")
        
        sucesso = self._capture.Initialize(enable_color, enable_depth, enable_ir)
        if not sucesso:
            logger.error("Não foi possível iniciar o Kinect. Verifique se ele está na USB 2.0/3.0 e ligado na tomada.")
        return sucesso

    def get_color_frame(self, bgr: bool = True) -> np.ndarray:
        """
        Retorna o frame de cor mais recente, ou None.
        Se enable_ir=True no start(), retorna matriz IR 16-bits.
        """
        if self._capture.IsFrameNew():
            raw_data = self._capture.GetLatestFrame()
            if raw_data:
                if self.is_ir:
                    # Array 16-bits (IR)
                    return np.frombuffer(raw_data, dtype=np.uint16).reshape(480, 640)
                else:
                    # Array 32-bits BGRA (Cor)
                    frame = np.frombuffer(raw_data, dtype=np.uint8).reshape(480, 640, 4)
                    if bgr:
                        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    return frame
        return None

    def get_depth_frame(self) -> np.ndarray:
        """
        Retorna o frame de profundidade (16-bits), ou None.
        """
        if hasattr(self._capture, 'IsDepthFrameNew') and self._capture.IsDepthFrameNew():
            raw_data = self._capture.GetLatestDepthFrame()
            if raw_data:
                return np.frombuffer(raw_data, dtype=np.uint16).reshape(480, 640)
        return None

    def set_tilt(self, angle: int) -> None:
        """Define a inclinação do motor (cravado entre -27 e 27)."""
        angle = max(-27, min(27, angle)) # Proteção de limites de hardware
        self._capture.SetTilt(angle)

    def get_tilt(self) -> int:
        """Retorna o ângulo de inclinação atual."""
        return self._capture.GetTilt()

    def stop(self) -> None:
        """Libera os recursos do hardware."""
        logger.info("Desligando hardware do Kinect...")
        self._capture.Stop()

    def test_motor(self) -> None:
        """Sequência automatizada de teste para o motor."""
        logger.info("Teste Motor: Olhando p/ Cima (+27°)")
        self.set_tilt(27)
        time.sleep(3)
        logger.info("Teste Motor: Olhando p/ Baixo (-27°)")
        self.set_tilt(-27)
        time.sleep(3)
        logger.info("Teste Motor: Centro (0°)")
        self.set_tilt(0)
        time.sleep(2)
        logger.info("Teste Motor: Finalizado.")
