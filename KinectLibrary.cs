using System;
using System.Linq;
using Microsoft.Kinect;
using System.Runtime.InteropServices;

namespace KinectInterop
{
    public class KinectCapture
    {
        private KinectSensor _sensor;
        private byte[] _colorPixels;
        private byte[] _depthPixels;
        private bool _newFrameAvailable = false;
        private bool _newDepthFrameAvailable = false;

        public bool Initialize(bool enableColor = true, bool enableDepth = false, bool enableIR = false)
        {
            _sensor = KinectSensor.KinectSensors.FirstOrDefault(s => s.Status == KinectStatus.Connected);
            if (_sensor == null) return false;

            if (enableIR) {
                _sensor.ColorStream.Enable(ColorImageFormat.InfraredResolution640x480Fps30);
                _sensor.ColorFrameReady += Sensor_ColorFrameReady;
            } else if (enableColor) {
                _sensor.ColorStream.Enable(ColorImageFormat.RgbResolution640x480Fps30);
                _sensor.ColorFrameReady += Sensor_ColorFrameReady;
            }

            if (enableDepth) {
                _sensor.DepthStream.Enable(DepthImageFormat.Resolution640x480Fps30);
                _sensor.DepthFrameReady += Sensor_DepthFrameReady;
            }

            try {
                _sensor.Start();
                return true;
            } catch {
                return false;
            }
        }

        private void Sensor_ColorFrameReady(object sender, ColorImageFrameReadyEventArgs e)
        {
            using (ColorImageFrame frame = e.OpenColorImageFrame())
            {
                if (frame != null)
                {
                    if (_colorPixels == null || _colorPixels.Length != frame.PixelDataLength) 
                        _colorPixels = new byte[frame.PixelDataLength];
                    frame.CopyPixelDataTo(_colorPixels);
                    _newFrameAvailable = true;
                }
            }
        }

        private void Sensor_DepthFrameReady(object sender, DepthImageFrameReadyEventArgs e)
        {
            using (DepthImageFrame frame = e.OpenDepthImageFrame())
            {
                if (frame != null)
                {
                    if (_depthPixels == null || _depthPixels.Length != frame.PixelDataLength * 2) 
                        _depthPixels = new byte[frame.PixelDataLength * 2];
                    short[] depthData = new short[frame.PixelDataLength];
                    frame.CopyPixelDataTo(depthData);
                    Buffer.BlockCopy(depthData, 0, _depthPixels, 0, depthData.Length * 2);
                    _newDepthFrameAvailable = true;
                }
            }
        }

        public byte[] GetLatestFrame()
        {
            _newFrameAvailable = false;
            return _colorPixels;
        }

        public byte[] GetLatestDepthFrame()
        {
            _newDepthFrameAvailable = false;
            return _depthPixels;
        }

        public bool IsFrameNew() => _newFrameAvailable;
        public bool IsDepthFrameNew() => _newDepthFrameAvailable;

        private int _currentTilt = 0;
        private bool _isTiltInitialized = false;

        public void SetTilt(int angle)
        {
            if (_sensor == null) return;
            
            // Limita o ângulo
            if (angle > 27) angle = 27;
            if (angle < -27) angle = -27;
            
            _currentTilt = angle; // Atualiza a variável local imediatamente

            // Executa em segundo plano
            System.Threading.Tasks.Task.Run(() => 
            {
                try {
                    _sensor.ElevationAngle = angle;
                } catch { }
            });
        }

        public int GetTilt()
        {
            // Na primeira vez, lê do hardware. Depois usa a variável em cache para não travar
            if (!_isTiltInitialized && _sensor != null) {
                try {
                    _currentTilt = _sensor.ElevationAngle;
                    _isTiltInitialized = true;
                } catch { }
            }
            return _currentTilt;
        }

        public void Stop()
        {
            if (_sensor != null) {
                _sensor.Stop();
            }
        }
    }
}
