from flask import Flask, Response, jsonify  
import subprocess
import numpy as np
from PIL import Image
import io
import threading
import time
from onvif import ONVIFCamera
from onvif.client import ONVIFService, ONVIFError
from urllib.parse import urlparse
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_rtsp_url(camera_ip, username, password):
    try:
        cam = ONVIFCamera(camera_ip, 80, username, password)
        media_service = cam.create_media_service()
        profiles = media_service.GetProfiles()
        
        stream_setup = {
            'StreamSetup': {
                'Stream': 'RTP-Unicast',
                'Transport': {'Protocol': 'RTSP'}
            },
            'ProfileToken': profiles[0].token
        }
        
        uri_info = media_service.GetStreamUri(stream_setup)
        parsed = urlparse(uri_info.Uri)
        
        # Добавляем логин:пароль в URL
        return f"rtsp://{username}:{password}@{parsed.netloc}{parsed.path}?{parsed.query}"
        
    except Exception as e:
        print(f"ONVIF Error: {str(e)}")
        return None

# Конфигурация камер
CAMERAS = {
    "cam1": {
        "ip": '192.168.2.134',
        "login": 'admin',
        "password": 'user1357',
        "rtspUrl": '',
        "width": 640,
        "height": 480,
        "running": False,
        "frame": None,
        "process": None,
        "thread": None
    },
    "cam2": {
        "ip": '192.168.2.137',
        "login": 'admin',
        "password": 'user1357',
        "rtspUrl": get_rtsp_url('192.168.2.137', 'admin', 'user1357'),
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
    
    if not camera['rtspUrl']:
        camera['rtspUrl'] = get_rtsp_url(camera['ip'], camera['login'], camera['password'])

    
    while camera['running']:
        try:
            cmd = [
                'ffmpeg',
                '-timeout', '5000000',
                '-rtsp_transport', 'tcp',
                '-i', camera['rtspUrl'],
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
    
@app.route('/status')
def camera_status():
    return jsonify({  # Используем jsonify вместо прямого возврата dict
        cam_id: {
            'running': CAMERAS[cam_id]['running'],
            'thread_alive': CAMERAS[cam_id]['thread'].is_alive() if CAMERAS[cam_id]['thread'] else False,
            'last_update': CAMERAS[cam_id].get('last_update')
        }
        for cam_id in CAMERAS
    })

# @app.route('/')
# def index():
#     return render_template('index.html', cameras=CAMERAS.keys())

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