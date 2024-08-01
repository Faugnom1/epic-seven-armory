import React, { useState, useEffect } from "react";
import "./sidebar.css";


const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(true);
  const [activeTab, setActiveTab] = useState(null);
  const [tabImages, setTabImages] = useState({});
  const [units, setUnits] = useState([]);

  
  useEffect(() => {
    const fetchImages = async (unitName) => {
        try{
            const response = await fetch('https://epic7db.com/api/heroes/' + unitName.replace(/ /g, '-') + '/mikeyfogs');
            const data = await response.json(); 
            setTabImages(image => ({...image, [unitName]: data.image}));
        } catch (error){
            console.error('Error fetching images:', error);
        }
    };

      const fetchData = async () => {
        const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcxNjg1ODkwOSwianRpIjoiNjBlNDMxNDMtYWIxZS00YTY1LThiNDUtNDgxZTJkODRkN2ZmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImZhdWdub20xIiwibmJmIjoxNzE2ODU4OTA5LCJjc3JmIjoiYTMzNmRjMzQtYmMwNy00YzI2LWE3MTItYzAxZjNlMDdkZGQyIn0.fBQFqL4-qHQHV39ZaUEpVw2TnaDIRqnldWFdwl0-n-8"
        try {
          const response = await fetch('https://epic-seven-armory.onrender.com/api/get_selected_units_data', {
            method: 'GET',
            headers: {
              'Authorization': 'Bearer ' + token
            }
          });
  
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
  
          const data = await response.json();

          setUnits(data); // Assuming `data` is the array of units
          setActiveTab(data[0].name); // Set the first unit as the active tab initially
          fetchImages(data?.[0]?.name);
          fetchImages(data?.[1]?.name);
          fetchImages(data?.[2]?.name);
          fetchImages(data?.[3]?.name);
        
        } catch (error) {
          console.log(error.message);
        }
      };


    fetchData();
  }, []);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const handleTabClick = (unitName) => {
    setActiveTab(unitName);
  };

return (
  <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
    <div className="toggle-button" onClick={toggleSidebar}>
      {isOpen ? '<<' : '>>'}
    </div>
    {isOpen && (
      <>
        <div>
          {units.length > 0 ? (
            <>
              <div className="tabs">
                {units.map((unit, index) => (
                  <button
                    style={{ backgroundImage: `url(${tabImages[unit.name]})` }}
                    key={index}
                    className={`tab-button ${activeTab === unit.name ? 'active' : ''}`}
                    onClick={() => handleTabClick(unit.name)}
                  >
                  </button>
                ))}
              </div>
              <div className="content">
                {units.map((unit, index) =>
                  activeTab === unit.name ? (
                    <div key={index} className="unit">
                      <h2>{unit.name}</h2>
                      <p>Attack: {unit.attack}</p>
                      <p>Defense: {unit.defense}</p>
                      <p>Health: {unit.health}</p>
                      <p>Speed: {unit.speed}</p>
                      <p>Critical Hit Chance: {unit.critical_hit_chance}</p>
                      <p>Critical Hit Damage: {unit.critical_hit_damage}</p>
                      <p>Effectiveness: {unit.effectiveness}</p>
                      <p>Effect Resistance: {unit.effect_resistance}</p>
                      {unit.set1 ? <p>Set: {unit.set1}</p> : ''}
                      {unit.set2 ? <p>Set: {unit.set2}</p> : ''}
                      {unit.set3 ? <p>Set: {unit.set3}</p> : ''}
                    </div>
                  ) : null
                )}
              </div>
            </>
          ) : (
            <div>Loading...</div>
          )}
        </div>
      </>
    )}
  </div>
);
};

export default Sidebar;
