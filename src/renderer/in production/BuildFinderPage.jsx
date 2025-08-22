import React, { useState, useEffect } from 'react';
import axios from 'axios';
import UnitStatsList from '../../components/UnitStatsList';

const BuildFinderPage = () => {
  const [units, setUnits] = useState([]);
  const ranks = ["Bronze", "Silver", "Gold", "Master", "Challenger", "Champion", "Emperor", "Legend"];
  const [formData, setFormData] = useState({
    unit: '',
    rank: ''
  });
  const [builds, setBuilds] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    axios.get('http://localhost:5000/get_unit_names')
      .then(response => {
        const uniqueUnits = [...new Set(response.data)];
        setUnits(uniqueUnits);

      })
      .catch(error => {
        console.error('There was an error fetching unit names!', error);
      });
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:5000/build_finder', formData, { withCredentials: true })
      .then(response => {
        setBuilds(response.data);
        setMessage('');
      })
      .catch(error => {
        if (error.response && error.response.status === 404) {
          setMessage('No data found for the selected unit and rank.');
          setBuilds(null);
        } else {
          console.error('There was an error fetching the builds!', error);
        }
      });
  };

  return (
    <div className="container">
      <h1>Build Finder</h1>
      <p>Select a unit and rank to find average stats.</p>
      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label htmlFor="unit">Unit:</label>
          <select
            name="unit"
            id="unit"
            className="form-control"
            value={formData.unit}
            onChange={handleChange}
          >
            <option value="">Select a unit</option>
            {units.map(name => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="rank">Rank:</label>
          <select
            name="rank"
            id="rank"
            className="form-control"
            value={formData.rank}
            onChange={handleChange}
          >
            <option value="">Select a rank</option>
            {ranks.map(rank => (
              <option key={rank} value={rank}>{rank}</option>
            ))}
          </select>
        </div>
        <button type="submit" className="btn btn-primary">Find Builds</button>
      </form>
      
      {builds && (
        <div className="mt-5">
          <h2>Average Stats for {formData.unit} at {formData.rank} Rank</h2>
          <UnitStatsList data={builds} />
        </div>
      )}
      {message && <div className="alert alert-info mt-3">{message}</div>}
    </div>
  );
};

export default BuildFinderPage;
