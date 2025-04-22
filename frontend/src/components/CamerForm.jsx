// components/CameraForm.jsx
import React, { useState } from 'react';

const CameraForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    ip: '',
    login: '',
    password: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
    setFormData({ ip: '', login: '', password: '' }); // Очищаем форму после отправки
  };

  return (
    <form onSubmit={handleSubmit} className="camera-form">
      <div className="form-group">
        <label>IP адрес:</label>
        <input
          type="text"
          name="ip"
          value={formData.ip}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="form-group">
        <label>Логин:</label>
        <input
          type="text"
          name="login"
          value={formData.login}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="form-group">
        <label>Пароль:</label>
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          required
        />
      </div>
      
      <button type="submit" className="submit-btn">Добавить камеру</button>
    </form>
  );
};

export default CameraForm;