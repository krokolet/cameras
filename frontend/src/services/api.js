// api.js
const API_BASE = 'http://localhost:5000';

export const getCameras = () => fetch(`${API_BASE}/status`);
export const getVideoFeed = (cameraId) => `${API_BASE}/video_feed/${cameraId}`;
export const addCamera = (cameraData) => {
    return fetch(`${API_BASE}/add_camera`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(cameraData),
    });
  };