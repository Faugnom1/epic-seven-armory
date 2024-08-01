import React, { useState } from 'react';
import axios from 'axios';

const SignupPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirm_password: '',
    epic_seven_account: '',
    streamer_name: '',
    rta_rank: ''
  });
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:5000/signup', formData)
      .then(response => {
        setMessage(response.data.message);
        // Redirect or perform other actions upon successful signup
      })
      .catch(error => {
        if (error.response) {
          setErrors(error.response.data.errors || {});
          setMessage(error.response.data.error || 'Signup failed');
        } else {
          console.error('There was an error signing up!', error);
        }
      });
  };

  return (
    <div className="container mt-5">
      <h2>Sign Up</h2>
      {message && <div className={`alert ${errors ? 'alert-danger' : 'alert-success'}`}>{message}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Username</label>
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
          <label className="form-label">Password</label>
          <input
            type="password"
            className={`form-control ${errors.password ? 'is-invalid' : ''}`}
            name="password"
            value={formData.password}
            onChange={handleChange}
          />
          {errors.password && <div className="invalid-feedback">{errors.password}</div>}
        </div>
        <div className="form-group">
          <label className="form-label">Confirm Password</label>
          <input
            type="password"
            className={`form-control ${errors.confirm_password ? 'is-invalid' : ''}`}
            name="confirm_password"
            value={formData.confirm_password}
            onChange={handleChange}
          />
          {errors.confirm_password && <div className="invalid-feedback">{errors.confirm_password}</div>}
        </div>
        <div className="form-group">
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
        <div className="form-group">
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
        <div className="form-group">
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
          <button type="submit" className="btn btn-primary">Sign Up</button>
        </div>
      </form>
    </div>
  );
};

export default SignupPage;
