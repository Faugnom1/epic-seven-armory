import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const UserProfile = () => {
  const { isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    epic_seven_account: '',
    streamer_name: '',
    rta_rank: ''
  });
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    axios.get('http://localhost:5000/profile', { withCredentials: true })
      .then(response => {
        setFormData(response.data);
      })
      .catch(error => {
        console.error('There was an error fetching the profile data!', error);
      });
  }, [isAuthenticated, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:5000/profile', formData, { withCredentials: true })
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(error => {
        if (error.response) {
          setErrors(error.response.data.errors);
        } else {
          console.error('There was an error updating the profile!', error);
        }
      });
  };

  return (
    <div className="container">
      <h2>User Profile</h2>
      {message && <div className="alert alert-success">{message}</div>}
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Username</label>
          <input
            type="text"
            className={`form-control ${errors.username ? 'is-invalid' : ''}`}
            name="username"
            value={formData.username}
            onChange={handleChange}
            readOnly
          />
          {errors.username && <div className="invalid-feedback">{errors.username}</div>}
        </div>
        <div className="mb-3">
          <label className="form-label">Epic Seven Account</label>
          <input
            type="text"
            className={`form-control ${errors.epic_seven_account ? 'is-invalid' : ''}`}
            name="epic_seven_account"
            value={formData.epic_seven_account}
            onChange={handleChange}
          />
          {errors.epic_seven_account && <div className="invalid-feedback">{errors.epic_seven_account}</div>}
        </div>
        <div className="mb-3">
          <label className="form-label">Streamer Name</label>
          <input
            type="text"
            className={`form-control ${errors.streamer_name ? 'is-invalid' : ''}`}
            name="streamer_name"
            value={formData.streamer_name}
            onChange={handleChange}
          />
          {errors.streamer_name && <div className="invalid-feedback">{errors.streamer_name}</div>}
        </div>
        <div className="mb-3">
          <label className="form-label">RTA Rank</label>
          <input
            type="text"
            className={`form-control ${errors.rta_rank ? 'is-invalid' : ''}`}
            name="rta_rank"
            value={formData.rta_rank}
            onChange={handleChange}
          />
          {errors.rta_rank && <div className="invalid-feedback">{errors.rta_rank}</div>}
        </div>
        <div>
          <button type="submit" className="btn btn-primary">Update Profile</button>
        </div>
      </form>
    </div>
  );
};

export default UserProfile;
