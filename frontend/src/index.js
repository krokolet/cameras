// frontend/src/index.js

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App'
import './index.css'; // Если используете CSS

// Создаем корневой рендер
const root = ReactDOM.createRoot(document.getElementById('root'));

// Рендерим главный компонент
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);