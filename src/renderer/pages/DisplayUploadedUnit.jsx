import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import UnitStatsList from '../components/UnitStatsList';

const DisplayUploadedUnit = () => {
  const [results, setResults] = useState([]);

  useEffect(() => {
    // Fetch the extracted stats from the backend
    axios.get('http://localhost:5000/display_stats')
      .then(response => {
        setResults(response.data);
      })
      .catch(error => {
        console.error('There was an error fetching the stats!', error);
      });
  }, []);

  return (
    <div className="container">
      <h1>Extracted Stats</h1>
      {results.map((result, index) => (
        <div key={index} className="stats-section">
          <h2>Stats for Image</h2>
          <UnitStatsList stats={result.stats} />
        </div>
      ))}
      <div className="text-center mt-4">
        <Link to="/upload" className="btn btn-primary">Upload Another Image</Link>
      </div>
    </div>
  );
};

export default DisplayUploadedUnit;
