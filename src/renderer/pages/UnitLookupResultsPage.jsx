import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';

const UnitLookupResultsPage = () => {
  const [unit, setUnit] = useState(null);
  const { unitName } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUnitData = async () => {
      try {
        const formattedUnitName = unitName.replace(' ', '-').toLowerCase();
        const apiUrl = `https://epic7db.com/api/heroes/${formattedUnitName}/mikeyfogs`;
        const response = await axios.get(apiUrl);

        if (response.status === 200) {
          setUnit(response.data);
          console.log(response.data)
        } else {
          console.error('Failed to fetch unit data');
        }
      } catch (error) {
        console.error('There was an error fetching the unit data!', error);
      }
    };

    fetchUnitData();
  }, [unitName]);

  if (!unit) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mt-5">
      <h1 className="display-4">{unit.name}</h1>
      <img src={unit.image} alt={`${unit.name} Image`} className="img-fluid mb-3" />
      <div className="section-box">
        <div className="row">
          <div className="col-md-6">
            <p><strong>Element:</strong> {unit.element}</p>
            <p><strong>Class:</strong> {unit.class}</p>
            <p><strong>Zodiac:</strong> {unit.zodiac}</p>
          </div>
        </div>
      </div>

      <div className="section-box">
        <h2 className="section-title">Base Stats</h2>
        <ul className="list-group list-group-flush">
          <li className="list-group-item"><strong>Attack:</strong> {unit.stats.attack}</li>
          <li className="list-group-item"><strong>Health:</strong> {unit.stats.health}</li>
          <li className="list-group-item"><strong>Defense:</strong> {unit.stats.defense}</li>
          <li className="list-group-item"><strong>Speed:</strong> {unit.stats.speed}</li>
        </ul>
      </div>

      <div className="section-box">
        <h2 className="section-title">Memory Imprints</h2>
        <div className="row">
          <div className="col-md-6">
            <h3 className="h6">Imprint Release</h3>
            <ul className="list-group list-group-flush">
              {Object.entries(unit.memory_imprints.imprint_release).map(([key, value]) => (
                <li key={key} className="list-group-item"><strong>{key}:</strong> {value}</li>
              ))}
            </ul>
          </div>
          <div className="col-md-6">
            <h3 className="h6">Imprint Concentration</h3>
            <ul className="list-group list-group-flush">
              {Object.entries(unit.memory_imprints.imprint_concentration).map(([key, value]) => (
                <li key={key} className="list-group-item"><strong>{key}:</strong> {value}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="section-box">
        <h2 className="section-title">Skills</h2>
        <ul className="list-group list-group-flush">
          {unit.skills.map(skill => (
            <li key={skill.name} className="list-group-item">
              <strong>{skill.name}</strong>: {skill.description}
            </li>
          ))}
        </ul>
      </div>
      <button className="btn btn-primary mt-3" onClick={() => navigate('/unit_lookup')}>Look Up Another Unit</button>
    </div>
  );
};

export default UnitLookupResultsPage;
