import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './renderer/components/Navbar';
import HomePage from './renderer/pages/HomePage';
import UploadUnit from './renderer/pages/UploadUnit';
import UnitLookupPage from './renderer/pages/UnitLookupPage';
import UnitLookupResultsPage from './renderer/pages/UnitLookupResultsPage';
import BuildFinderPage from './renderer/pages/BuildFinderPage';
import YourUnitsPage from './renderer/pages/YourUnitsPage';
import SignupPage from './renderer/pages/SignupPage';
import LoginPage from './renderer/pages/LoginPage';
import UserProfile from './renderer/pages/UserProfile';
import DisplayUploadedUnit from './renderer/pages/DisplayUploadedUnit';
import Logout from './renderer/components/Logout';
import TwitchOverlay from './renderer/pages/TwitchOverlay';
import { AuthProvider } from './renderer/context/AuthContext';
import Sidebar from './renderer/sidebar/Sidebar';
import './renderer/css/App.css';

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <div>
          <Navbar />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<UploadUnit />} />
            <Route path="/unit_lookup" element={<UnitLookupPage />} />
            <Route path="/unit_details/:unitName" element={<UnitLookupResultsPage />} />
            <Route path="/build_finder" element={<BuildFinderPage />} />
            <Route path="/your_units" element={<YourUnitsPage />} />
            <Route path="/profile" element={<UserProfile />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/user_profile" element={<UserProfile />} />
            <Route path="/display_uploaded_unit" element={<DisplayUploadedUnit />} />
            <Route path="/overlay" element={<TwitchOverlay />} />
            <Route path="/sidebar" element={<Sidebar />} />
            <Route path="/logout" element={<Logout />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
