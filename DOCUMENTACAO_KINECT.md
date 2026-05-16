# Documentação: Biblioteca Kinect V1 (Python/C#)

Esta biblioteca foi construída para facilitar o uso do sensor Kinect V1 no Python (usando o módulo `kinect_lib.py`), com as rotinas de baixo nível executadas por uma DLL C# otimizada (`KinectInterop.dll`).

## 0. Requisitos de Sistema para Qualquer PC
Para garantir que esse projeto rode em **qualquer computador**, verifique se a máquina atende os seguintes requisitos antes de executar o Python:

1. **Windows 10 ou Windows 11 (x64)**.
2. **Microsoft Kinect SDK v1.8 Instalado**. Baixe do site oficial da Microsoft e instale o `.exe`. Ele contém os drivers essenciais.
3. **Python 3.8 a 3.11 (x64)**. Certifique-se de que é a versão de 64-bits.
4. **Instalar Dependências**. Abra o terminal na pasta do projeto e rode:
   ```bash
   pip install -r requirements.txt
   ```
5. **A DLL C# Precisa Estar Compilada**. Certifique-se de ter rodado `dotnet build KinectConsole.csproj` na máquina destino ao menos uma vez.

---

## 1. Importação Básica
Para usar em qualquer script Python seu, basta colocar o arquivo `kinect_lib.py` na mesma pasta e importar a classe principal:

```python
from KinectLib.kinect_lib import KinectSensor
kinect = KinectSensor()
```

---

## 2. Palavras-chave e Regras de Ouro
- **RGB (Color)**: É a câmera colorida normal. Retorna uma imagem com formato `(480, 640, 3)` (se usar `bgr=True`) ou `(480, 640, 4)` (se usar `bgr=False`).
- **IR (Infravermelho)**: É a câmera noturna. Retorna uma matriz 2D bruta de 16-bits `(480, 640)`. Precisa ser convertida para 8-bits para exibir na tela (ex: usando `(frame_ir >> 8).astype(np.uint8)`).
- **Depth (Profundidade)**: É o sensor 3D. Retorna uma matriz 2D bruta de 16-bits `(480, 640)`, onde o valor de cada pixel é a distância real em milímetros.
- **REGRA CRÍTICA**: Você **NÃO PODE** usar `enable_color=True` e `enable_ir=True` ao mesmo tempo. O Kinect V1 compartilha a mesma banda/lente para os dois. Já o `enable_depth` pode ser usado com qualquer um dos dois (ex: RGB + Depth ou IR + Depth).

---

## 3. Documentação das Funções (API)

### `kinect.start(enable_color=True, enable_depth=False, enable_ir=False)`
Liga o sensor e inicializa os fluxos escolhidos. Retorna `True` se funcionou.

### `kinect.get_color_frame(bgr=True)`
Pega o frame atual da câmera (RGB ou IR, dependendo do que ativou).

### `kinect.get_depth_frame()`
Pega o mapa de profundidade bruto atual em milímetros (16-bits).

### `kinect.set_tilt(angle)`
Move a "cabeça" motorizada do Kinect (-27 a +27).

### `kinect.get_tilt()`
Retorna a inclinação atual (inteiro).

### `kinect.stop()`
Desliga o sensor de forma limpa. Sempre chame no final!

### `kinect.test_motor()`
Faz o teste automático de limite do motor.

---

## 4. Exemplos Práticos de Uso

### Exemplo 1: Só Imagem RGB Normal (O Básico)
```python
import cv2
from KinectLib.kinect_lib import KinectSensor

kinect = KinectSensor()
if kinect.start(enable_color=True): # Liga apenas a cor
    try:
        while True:
            frame = kinect.get_color_frame()
            if frame is not None:
                cv2.imshow("Kinect RGB", frame)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        kinect.stop()
        cv2.destroyAllWindows()
```

### Exemplo 2: Usando o Infravermelho (IR) no Escuro
```python
import cv2
import numpy as np
from KinectLib.kinect_lib import KinectSensor

kinect = KinectSensor()
# Liga APENAS o IR. (Lembrando: Cor precisa ser False)
if kinect.start(enable_color=False, enable_ir=True):
    try:
        while True:
            frame_ir = kinect.get_color_frame()
            if frame_ir is not None:
                # Converte os 16-bits pra 8-bits para o OpenCV conseguir desenhar a tela
                frame_8u = (frame_ir >> 8).astype(np.uint8)
                cv2.imshow("Kinect IR", frame_8u)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        kinect.stop()
        cv2.destroyAllWindows()
```

### Exemplo 3: Lendo o Mapa de Profundidade (Distância em 3D)
```python
import cv2
import numpy as np
from KinectLib.kinect_lib import KinectSensor

kinect = KinectSensor()
# Liga Cor e Depth (Profundidade)
if kinect.start(enable_color=True, enable_depth=True):
    try:
        while True:
            frame_rgb = kinect.get_color_frame()
            frame_depth = kinect.get_depth_frame()
            
            if frame_rgb is not None:
                cv2.imshow("Kinect RGB", frame_rgb)
                
            if frame_depth is not None:
                # Depth vem em milimetros (16-bits). Convertendo pra 8-bits
                # Multiplicamos e dividimos pra mapear visualmente e aplicamos mapa de cor
                depth_8u = (frame_depth / 32).astype(np.uint8) 
                depth_colorida = cv2.applyColorMap(depth_8u, cv2.COLORMAP_JET)
                
                cv2.imshow("Kinect Profundidade", depth_colorida)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        kinect.stop()
        cv2.destroyAllWindows()
```

### Exemplo 4: Movendo o Motor de Inclinação pelo Teclado
```python
import cv2
from KinectLib.kinect_lib import KinectSensor

kinect = KinectSensor()
if kinect.start(enable_color=True):
    try:
        print("Aperte W para subir e S para descer. Q para sair.")
        while True:
            frame = kinect.get_color_frame()
            if frame is not None:
                cv2.imshow("Controle de Motor", frame)
                
            key = cv2.waitKey(1) & 0xFF
            if key == ord('w'):
                atual = kinect.get_tilt()
                kinect.set_tilt(atual + 5) # Sobe 5 graus
                print(f"Inclinação: {kinect.get_tilt()}°")
            elif key == ord('s'):
                atual = kinect.get_tilt()
                kinect.set_tilt(atual - 5) # Desce 5 graus
                print(f"Inclinação: {kinect.get_tilt()}°")
            elif key == ord('q'):
                break
    finally:
        kinect.stop()
        cv2.destroyAllWindows()
```
