using System;
using System.Linq;
using Microsoft.Kinect;
using System.Runtime.InteropServices;
using System.Threading;

namespace KinectConsoleKeyboard
{
    class Program
    {
        // Configurações do Kinect
        private static KinectSensor _sensor;
        private const int MinDepth = 450;
        private const int MaxDepth = 1500;
        
        // ROI (Área da Mesa)
        private const int RoiX = 150;
        private const int RoiY = 100;
        private const int RoiWidth = 340;
        private const int RoiHeight = 280;

        // Lógica de Teclado
        private static DateTime _lastTrigger = DateTime.MinValue;
        
        [DllImport("user32.dll")]
        private static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, int dwExtraInfo);
        private const uint KEYEVENTF_KEYUP = 0x0002;

        static void Main(string[] args)
        {
            _sensor = KinectSensor.KinectSensors.FirstOrDefault(s => s.Status == KinectStatus.Connected);

            if (_sensor == null)
            {
                Console.WriteLine("ERRO: Kinect não encontrado!");
                return;
            }

            // Habilita apenas o Stream de Profundidade (Depth)
            _sensor.DepthStream.Enable(DepthImageFormat.Resolution640x480Fps30);
            _sensor.DepthFrameReady += Sensor_DepthFrameReady;

            try
            {
                _sensor.Start();
                Console.WriteLine("KINECT ONLINE");

                // --- TESTE DO MOTOR ---
                Console.WriteLine("Testando Motor (Tilt)... subindo");
                _sensor.ElevationAngle = 15; // Sobe 15 graus
                Thread.Sleep(2000);
                
                Console.WriteLine("Testando Motor (Tilt)... descendo");
                _sensor.ElevationAngle = -15; // Desce 15 graus
                Thread.Sleep(2000);
                
                _sensor.ElevationAngle = 0; // Volta ao centro
                Console.WriteLine("Motor OK. Voltando ao centro.");
                // ----------------------

                Console.WriteLine("Mapeando área: {0},{1} com {2}x{3}", RoiX, RoiY, RoiWidth, RoiHeight);
                Console.WriteLine("Pressione CTRL+C para encerrar.");
            }
            catch (Exception ex)
            {
                Console.WriteLine("ERRO FATAL: " + ex.Message);
                return;
            }

            // Loop para manter o processo vivo
            while (true)
            {
                Thread.Sleep(1000);
            }
        }

        private static void Sensor_DepthFrameReady(object sender, DepthImageFrameReadyEventArgs e)
        {
            using (DepthImageFrame frame = e.OpenDepthImageFrame())
            {
                if (frame == null) return;

                short[] depthData = new short[frame.PixelDataLength];
                frame.CopyPixelDataTo(depthData);
                
                ProcessDepth(depthData, frame.Width, frame.Height);
            }
        }

        private static void ProcessDepth(short[] depthData, int width, int height)
        {
            int minDepthFound = int.MaxValue;

            // Busca a menor profundidade na ROI
            for (int y = RoiY; y < RoiY + RoiHeight; y += 4)
            {
                for (int x = RoiX; x < RoiX + RoiWidth; x += 4)
                {
                    int index = x + (y * width);
                    short depth = (short)(depthData[index] >> 3);
                    if (depth > MinDepth && depth < MaxDepth && depth < minDepthFound)
                        minDepthFound = depth;
                }
            }

            if (minDepthFound == int.MaxValue) return;

            long sumX = 0, sumY = 0;
            int count = 0;

            // Calcula centro de massa dos pixels próximos à profundidade mínima
            for (int y = RoiY; y < RoiY + RoiHeight; y += 2)
            {
                for (int x = RoiX; x < RoiX + RoiWidth; x += 2)
                {
                    int index = x + (y * width);
                    short depth = (short)(depthData[index] >> 3);

                    if (depth > MinDepth && depth <= minDepthFound + 50)
                    {
                        sumX += x;
                        sumY += y;
                        count++;
                    }
                }
            }

            if (count < 10) return;

            int targetX = width - (int)(sumX / count); // Espelhado
            int targetY = (int)(sumY / count);

            AnalyzePosition(targetX, targetY);
        }

        private static void AnalyzePosition(int x, int y)
        {
            int col = ((x - RoiX) * 3) / RoiWidth;
            int row = ((y - RoiY) * 3) / RoiHeight;

            // Mapeamento de teclas QWE, ASD, ZXC
            byte[,] keys = {
                { 0x51, 0x57, 0x45 }, 
                { 0x41, 0x53, 0x44 }, 
                { 0x5A, 0x58, 0x43 }  
            };

            if (row >= 0 && row < 3 && col >= 0 && col < 3)
            {
                TriggerKey(keys[row, col]);
            }
        }

        private static void TriggerKey(byte key)
        {
            if ((DateTime.Now - _lastTrigger).TotalMilliseconds > 800)
            {
                keybd_event(key, 0, 0, 0); // Down
                keybd_event(key, 0, KEYEVENTF_KEYUP, 0); // Up
                _lastTrigger = DateTime.Now;
                Console.WriteLine("Key: " + (char)key);
            }
        }
    }
}
