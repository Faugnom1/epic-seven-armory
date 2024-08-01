import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const UnitLookupPage = () => {
  const [units, setUnits] = useState([]);
  const [selectedUnit, setSelectedUnit] = useState('');
  const navigate = useNavigate();

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
    setSelectedUnit(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedUnit) {
      navigate(`/unit_details/${selectedUnit}`);
    }
  };

  return (
    <div className="container">
      <h1>Unit Look Up</h1>
      <p>Find base stats, imprint values, and skill information.</p>
      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label htmlFor="unit">Unit:</label>
          <select name="unit" id="unit" className="form-control" value={selectedUnit} onChange={handleChange}>
            <option value="">Select a unit</option>
            {units.map(name => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </div>
        <button type="submit" className="btn btn-primary">Search</button>
      </form>
    </div>
  );
};

export default UnitLookupPage;
