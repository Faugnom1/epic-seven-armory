import React from 'react';

const UnitStatsList = ({ data }) => {
  if (!data) {
    return <div>No unit selected</div>;
  }

  if (!data.attack)
    return (
    <ul className="list-group list-group-flush">
      <li className="list-group-item"><strong>Attack: </strong>{data[0].attack}</li>
      <li className="list-group-item"><strong>Defense: </strong>{data[0].defense}</li>
      <li className="list-group-item"><strong>Health: </strong>{data[0].health}</li>
      <li className="list-group-item"><strong>Speed: </strong>{data[0].speed}</li>
      <li className="list-group-item"><strong>Critical Hit Chance: </strong>{data[0].critical_hit_chance}</li>
      <li className="list-group-item"><strong>Critical Hit Damage: </strong>{data[0].critical_hit_damage}</li>
      <li className="list-group-item"><strong>Effectiveness: </strong>{data[0].effectiveness}</li>
      <li className="list-group-item"><strong>Effect Resistance: </strong>{data[0].effect_resistance}</li>
      <li className="list-group-item"><strong>Set 1: </strong>{data[0].set1}</li>
      <li className="list-group-item"><strong>Set 2: </strong>{data[0].set2}</li>
      <li className="list-group-item"><strong>Set 3: </strong>{data[0].set3}</li>
    </ul>
  );

  else
    return (
      <ul className="list-group list-group-flush">
        <li className="list-group-item"><strong>Attack: </strong>{data.attack}</li>
        <li className="list-group-item"><strong>Defense: </strong>{data.defense}</li>
        <li className="list-group-item"><strong>Health: </strong>{data.health}</li>
        <li className="list-group-item"><strong>Speed: </strong>{data.speed}</li>
        <li className="list-group-item"><strong>Critical Hit Chance: </strong>{data.critical_hit_chance}</li>
        <li className="list-group-item"><strong>Critical Hit Damage: </strong>{data.critical_hit_damage}</li>
        <li className="list-group-item"><strong>Effectiveness: </strong>{data.effectiveness}</li>
        <li className="list-group-item"><strong>Effect Resistance: </strong>{data.effect_resistance}</li>
        <li className="list-group-item"><strong>Set 1: </strong>{data.set1}</li>
        <li className="list-group-item"><strong>Set 2: </strong>{data.set2}</li>
        <li className="list-group-item"><strong>Set 3: </strong>{data.set3}</li>
      </ul>
    );

};

export default UnitStatsList;
