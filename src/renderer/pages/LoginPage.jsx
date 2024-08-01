import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');
  const navigate = useNavigate();
  const { setIsAuthenticated } = useAuth();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:5000/login', formData, { withCredentials: true })
      .then(response => {
        setMessage(response.data.message);
        setIsAuthenticated(true); // Set authentication state
        navigate('/');
      })
      .catch(error => {
        if (error.response) {
          setErrors(error.response.data.errors || {});
          setMessage(error.response.data.error || 'Login failed');
        } else {
          console.error('There was an error logging in!', error);
        }
      });
  };

  return (
    <div className="container mt-5">
      <h2>Log In</h2>
      {message && <div className={`alert ${errors ? 'alert-danger' : 'alert-success'}`}>{message}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username</label>
          <input
            type="text"
            className={`form-control ${errors.username ? 'is-invalid' : ''}`}
            name="username"
            value={formData.username}
            onChange={handleChange}
          />
          {errors.username && <div className="invalid-feedback">{errors.username}</div>}
        </div>
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            className={`form-control ${errors.password ? 'is-invalid' : ''}`}
            name="password"
            value={formData.password}
            onChange={handleChange}
          />
          {errors.password && <div className="invalid-feedback">{errors.password}</div>}
        </div>
        <div>
          <button type="submit" className="btn btn-primary">Log In</button>
        </div>
      </form>
    </div>
  );
};

export default LoginPage;
