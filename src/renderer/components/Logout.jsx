import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Logout = ({ setIsAuthenticated }) => {
  const navigate = useNavigate();

  useEffect(() => {
    setIsAuthenticated(false);
    navigate('/');
  }, [navigate, setIsAuthenticated]);

  return null;
};

export default Logout;
