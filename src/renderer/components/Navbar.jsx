
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../css/Navbar.css';

const Navbar = () => {
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className="navbar">
      <Link className="navbar-brand" to="/">E7 Armory</Link>
      <ul className="nav-menu">
        {isAuthenticated ? (
          <>
            <li className="nav-item"><Link className="nav-link" to="/upload">Upload Image</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/unit_lookup">Unit Look Up</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/build_finder">Build Finder</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/your_units">Your Units</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/profile">User Profile</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/overlay">Twitch Overlay Setup</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/sidebar">Sidebar</Link></li>
            <li className="nav-item"><Link className="nav-link" onClick={logout}>Log Out</Link></li>
          </>
        ) : (
          <>
            <li className="nav-item"><Link className="nav-link" to="/signup">Sign Up</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/login">Log In</Link></li>
          </>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;
