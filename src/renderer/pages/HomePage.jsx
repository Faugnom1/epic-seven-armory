import React from 'react';

const HomePage = () => (
  <div className="container">
    <h1>E7 Armory</h1>
    <div className="intro">
      Dive into the vast world of "Epic Seven" with your one-stop portal for optimizing your gameplay and displaying your hard work to your Twitch.tv audience.
    </div>
    <br></br>
    <h2>Features:</h2>
    <ul className="features-list">
      <li><strong>Stat Extraction:</strong> Extract stats directly from screenshots without the hassle of manual data entry.</li>
      <li><strong>Build Finder:</strong> Search through an extensive database to find average builds based on unit and rank.</li>
      <li><strong>User Profiles:</strong> Create and manage your profile, store favorite units, and keep track of your builds all in one place.</li>
      <li><strong>Dynamic Updates:</strong> Stay up-to-date with the latest unit stats and rankings as the Epic Seven universe expands and evolves.</li>
      <li><strong>Twitch Overlay:</strong> Once your units are uploaded and your profile is set, easily display your units in arena and guild battles with our Twitch Overlay.</li>
    </ul>
  </div>
);

export default HomePage;