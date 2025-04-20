from flask import Flask, Response, render_template
import subprocess
import numpy as np
from PIL import Image
import io
import threading
import time

app = Flask(__name__)

# Конфигурация камер
CAMERAS = {
    "cam1": {
        "url": "rtsp://admin:user1357@192.168.2.134/stream1",
        "width": 640,
        "height": 480,
        "running": False,
        "frame": None,
        "process": None,
        "thread": None
    },
    "cam2": {
        "url": "rtsp://admin:user1357@192.168.2.137/stream1",
        "width": 640,
        "height": 480,
        "running": False,
        "frame": None,
        "process": None,
        "thread": None
    }
}

def camera_stream(camera_id):
    """Функция для захвата потока с камеры в отдельном потоке"""
    camera = CAMERAS[camera_id]
    
    while camera['running']:
        try:
            cmd = [
                'ffmpeg',
                '-timeout', '5000000',
                '-rtsp_transport', 'tcp',
                '-i', camera['url'],
                '-f', 'image2pipe',
                '-pix_fmt', 'rgb24',
                '-vcodec', 'rawvideo',
                '-r', '10',
                '-vf', f'scale={camera["width"]}:{camera["height"]}',
                '-'
            ]
            
            camera['process'] = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=camera['width'] * camera['height'] * 3
            )

            while camera['running']:
                raw_frame = camera['process'].stdout.read(camera['width'] * camera['height'] * 3)
                if not raw_frame:
                    break
                    
                frame = np.frombuffer(raw_frame, dtype=np.uint8)
                camera['frame'] = frame.reshape((camera['height'], camera['width'], 3))

        except Exception as e:
            print(f"Ошибка камеры {camera_id}: {str(e)}")
            time.sleep(2)

        finally:
            if camera['process']:
                camera['process'].terminate()

def start_camera_threads():
    """Запуск потоков для камер"""
    for cam_id in CAMERAS:
        if not CAMERAS[cam_id]['thread'] or not CAMERAS[cam_id]['thread'].is_alive():
            CAMERAS[cam_id]['running'] = True
            CAMERAS[cam_id]['thread'] = threading.Thread(
                target=camera_stream,
                args=(cam_id,),
                daemon=True
            )
            CAMERAS[cam_id]['thread'].start()

# Запускаем потоки при первом запросе
@app.before_request
def before_first_request():
    if not hasattr(app, 'cameras_started'):
        start_camera_threads()
        app.cameras_started = True

@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    def generate():
        while True:
            frame = CAMERAS[camera_id]['frame']
            if frame is not None:
                img = Image.fromarray(frame)
                buf = io.BytesIO()
                img.save(buf, format='JPEG', quality=85)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buf.getvalue() + b'\r\n')
            else:
                blank_frame = np.zeros((CAMERAS[camera_id]['height'], CAMERAS[camera_id]['width'], 3), dtype=np.uint8)
                img = Image.fromarray(blank_frame)
                buf = io.BytesIO()
                img.save(buf, format='JPEG')
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buf.getvalue() + b'\r\n')
            time.sleep(0.1)

    return Response(generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html', cameras=CAMERAS.keys())

@app.route('/stop')
def stop():
    """Для остановки (для тестирования)"""
    for cam_id in CAMERAS:
        CAMERAS[cam_id]['running'] = False
        if CAMERAS[cam_id]['thread']:
            CAMERAS[cam_id]['thread'].join(timeout=1)
    return "Потоки камер остановлены"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)