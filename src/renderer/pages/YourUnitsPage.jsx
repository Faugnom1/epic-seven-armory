import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import UnitStatsList from '../components/UnitStatsList';

const YourUnitsPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [units, setUnits] = useState([]);
  const [selectedUnit, setSelectedUnit] = useState(null);
  const [unitIdToDelete, setUnitIdToDelete] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    // Fetch the user's units from the backend
    axios.get('http://localhost:5000/your_units', { withCredentials: true })
      .then(response => {
        setUnits(response.data);
      })
      .catch(error => {
        console.error('There was an error fetching the units!', error);
      });
  }, [isAuthenticated, navigate]);

  const handleViewStats = (e) => {
    e.preventDefault();
    const unitName = e.target.unit.value;
    axios.post('http://localhost:5000/your_units', { unit: unitName }, { withCredentials: true })
      .then(response => {
        setSelectedUnit(response.data);
        console.log(response.data)
      })
      .catch(error => {
        console.error('There was an error fetching the unit stats!', error);
      });
  };

  const handleDeleteUnit = (e) => {
    console.log(unitIdToDelete)
    e.preventDefault();
    axios.post('http://localhost:5000/delete_unit', { unit_to_delete: unitIdToDelete }, { withCredentials: true })
      .then(response => {
        setMessage(response.data.message);
        setUnits(units.filter(unit => unit.id !== parseInt(unitIdToDelete)));
        setUnitIdToDelete('');
        setSelectedUnit(null);
      })
      .catch(error => {
        console.error('There was an error deleting the unit!', error);
      });
  };

  const handleSelectChange = (e) => {
    setUnitIdToDelete(e.target.value);
  };

  return (
    <div className="container">
      {selectedUnit && (
        <>
          <h2>{selectedUnit.unit}</h2>
          <div className="stats-section">
            <UnitStatsList data={selectedUnit} />
          </div>
          <a href={`http://localhost:5000/display_unit/${selectedUnit.unit}`} className="btn btn-info">Unit Look Up for {selectedUnit.unit}</a>
          <br />
        </>
      )}
      <h2>Your Units</h2>
      <form onSubmit={handleViewStats}>
        <select name="unit" className="form-control mt-3">
          {units.map(unit => (
            <option key={unit.unit} value={unit.unit}>{unit.unit}</option>
          ))}
        </select>
        <button type="submit" className="btn btn-info mt-3">View Stats</button>
      </form>
      <br />
      <h2>Delete a Unit</h2>
      <form onSubmit={handleDeleteUnit}>
        <div className="form-group">
          <label htmlFor="unit_to_delete">Select Unit to Delete</label>
          <select name="unit_to_delete" className="form-control mt-3" value={unitIdToDelete} onChange={handleSelectChange}>
            {units.map(unit => (
              <option key={unit.id} value={unit.id}>{unit.unit}</option>
            ))}
          </select>
        </div>
        <button type="submit" className="btn btn-danger mt-3">Delete Unit</button>
      </form>
      {message && <div className="alert alert-success mt-3">{message}</div>}
    </div>
  );
};

export default YourUnitsPage;
