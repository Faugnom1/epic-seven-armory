import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import UnitStatsList from '../components/UnitStatsList';
import { useNavigate } from 'react-router-dom';

const UploadUnit = () => {
  const { isAuthenticated } = useAuth();
  const [localFiles, setLocalFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const navigate = useNavigate();

  const handleLocalFileChange = (e) => {
    setLocalFiles(e.target.files);
  };

  const handleLocalUpload = (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      alert('You must be logged in to upload files.');
      return;
    }

    setLoading(true);

    const formData = new FormData();
    for (let i = 0; i < localFiles.length; i++) {
      formData.append('file', localFiles[i]);
    }

    axios.post('http://localhost:5000/upload_file', formData, { withCredentials: true })
      .then(() => {
        axios.get('http://localhost:5000/display', { withCredentials: true })
          .then(response => {
            setLoading(false); 
            setStats(response.data);
            console.log(response.data)
          })
          .catch(error => {
            setLoading(false);
            console.error('There was an error fetching the data!', error);
          });
      })
      .catch(error => {
        setLoading(false);
        console.error('There was an error uploading the files locally!', error);
        alert('There was an error uploading the files.');
      });
  };

  useEffect(() => {
    if (stats) {
      console.log(stats);
    }
  }, [stats]);

  return (
    <div className="container">
      <h1>Scan an Image</h1>
      <form onSubmit={handleLocalUpload} encType="multipart/form-data">
        <div className="form-group">
          <label htmlFor="file"></label>
          <h2>Screenshot must not be cropped:</h2>
          <input type="file" name="file" multiple required className="form-control" onChange={handleLocalFileChange} />
        </div>
        <button type="submit" className="btn btn-primary mt-3">Analyze Image</button>
      </form>
      <hr />
      {loading && (
        <div id="overlay">
          <div id="overlayText">Please wait...</div>
        </div>
      )}
      {stats && (
        <div className="mt-5">
          <h2>Extracted Stats</h2>
          <UnitStatsList data={stats}/>
        </div>
      )}
    </div>
  );
};

export default UploadUnit;
