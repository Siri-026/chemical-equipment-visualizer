import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import './App.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';



function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [equipmentList, setEquipmentList] = useState([]);
  const [history, setHistory] = useState([]);
  const [selectedUploadId, setSelectedUploadId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [darkMode, setDarkMode] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (token) {
      setIsAuthenticated(true);
      fetchHistory();
    }
  }, [token]);

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const endpoint = isLogin ? '/auth/login/' : '/auth/register/';
      const response = await axios.post(`${API_BASE_URL}${endpoint}`, {
        username,
        password
      });
      
      setToken(response.data.token);
      localStorage.setItem('token', response.data.token);
      setIsAuthenticated(true);
      setMessage(`${isLogin ? 'Login' : 'Registration'} successful!`);
    } catch (error) {
      setMessage(error.response?.data?.error || 'Authentication failed');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    setToken('');
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setSummary(null);
    setEquipmentList([]);
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage('Please select a file');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          ...(token && { 'Authorization': `Token ${token}` })
        }
      });

      setSummary(response.data.summary);
      setSelectedUploadId(response.data.upload_id);
      setMessage('File uploaded successfully!');
      fetchEquipmentList(response.data.upload_id);
      fetchHistory();
    } catch (error) {
      setMessage(error.response?.data?.error || 'Upload failed');
    }
    setLoading(false);
  };

  const fetchEquipmentList = async (uploadId = null) => {
    try {
      const url = uploadId ? `${API_BASE_URL}/equipment/?upload_id=${uploadId}` : `${API_BASE_URL}/equipment/`;
      const response = await axios.get(url, {
        headers: token ? { 'Authorization': `Token ${token}` } : {}
      });
      setEquipmentList(response.data);
    } catch (error) {
      console.error('Error fetching equipment list:', error);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/history/`, {
        headers: token ? { 'Authorization': `Token ${token}` } : {}
      });
      setHistory(response.data);
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  const loadHistoryData = async (uploadId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/summary/?upload_id=${uploadId}`, {
        headers: token ? { 'Authorization': `Token ${token}` } : {}
      });
      setSummary({
        total_count: response.data.total_count,
        avg_flowrate: response.data.avg_flowrate,
        avg_pressure: response.data.avg_pressure,
        avg_temperature: response.data.avg_temperature,
        type_distribution: response.data.type_distribution
      });
      setSelectedUploadId(uploadId);
      fetchEquipmentList(uploadId);
    } catch (error) {
      setMessage('Error loading history data');
    }
    setLoading(false);
  };

  const downloadPDF = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/generate-report/`, 
        { upload_id: selectedUploadId },
        { 
          responseType: 'blob',
          headers: token ? { 'Authorization': `Token ${token}` } : {}
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `equipment_report_${selectedUploadId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setMessage('PDF downloaded successfully!');
    } catch (error) {
      setMessage('Error generating PDF');
    }
    setLoading(false);
  };

  const downloadExcel = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/export-excel/`, 
        { upload_id: selectedUploadId },
        { 
          responseType: 'blob',
          headers: token ? { 'Authorization': `Token ${token}` } : {}
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `equipment_data_${selectedUploadId}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setMessage('Excel downloaded successfully!');
    } catch (error) {
      setMessage('Error generating Excel file');
    }
    setLoading(false);
  };

  const pieChartData = summary?.type_distribution ? {
    labels: Object.keys(summary.type_distribution),
    datasets: [{
      label: 'Equipment Type Distribution',
      data: Object.values(summary.type_distribution),
      backgroundColor: [
        'rgba(255, 99, 132, 0.6)',
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 206, 86, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(153, 102, 255, 0.6)',
      ],
      borderWidth: 1,
    }]
  } : null;

  const barChartData = summary ? {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [{
      label: 'Average Values',
      data: [summary.avg_flowrate, summary.avg_pressure, summary.avg_temperature],
      backgroundColor: [
        'rgba(75, 192, 192, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(153, 102, 255, 0.6)',
      ],
      borderWidth: 1,
    }]
  } : null;

  if (!isAuthenticated) {
    return (
      <div className="App">
        <div className="auth-container">
          <h1>Chemical Equipment Visualizer</h1>
          <div className="auth-form">
            <h2>{isLogin ? 'Login' : 'Register'}</h2>
            <form onSubmit={handleAuth}>
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Processing...' : (isLogin ? 'Login' : 'Register')}
              </button>
            </form>
            <p className="toggle-auth">
              {isLogin ? "Don't have an account? " : "Already have an account? "}
              <span onClick={() => setIsLogin(!isLogin)}>
                {isLogin ? 'Register' : 'Login'}
              </span>
            </p>
            {message && <p className="message">{message}</p>}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`App ${darkMode ? 'dark-mode' : ''}`}>
      <header className="App-header">
        <h1>Chemical Equipment Parameter Visualizer</h1>
        <div className="header-buttons">
          <button onClick={() => setDarkMode(!darkMode)} className="theme-btn">
            {darkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
          </button>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <div className="container">
        <section className="upload-section">
          <h2>Upload CSV File</h2>
          <form onSubmit={handleUpload}>
            <input type="file" accept=".csv" onChange={handleFileChange} />
            <button type="submit" disabled={loading}>
              {loading ? 'Uploading...' : 'Upload'}
            </button>
          </form>
          {message && <p className="message">{message}</p>}
        </section>

        {history.length > 0 && (
          <section className="history-section">
            <h2>Upload History</h2>
            <div className="history-list">
              {history.map((item) => (
                <div 
                  key={item.id} 
                  className={`history-item ${selectedUploadId === item.id ? 'active' : ''}`}
                  onClick={() => loadHistoryData(item.id)}
                >
                  <strong>{item.filename}</strong>
                  <span>{new Date(item.uploaded_at).toLocaleString()}</span>
                  <span>Count: {item.total_count}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {summary && (
          <>
            <section className="summary-section">
              <h2>Data Summary</h2>
              <div className="summary-cards">
                <div className="card">
                  <h3>Total Equipment</h3>
                  <p>{summary.total_count}</p>
                </div>
                <div className="card">
                  <h3>Avg Flowrate</h3>
                  <p>{summary.avg_flowrate}</p>
                </div>
                <div className="card">
                  <h3>Avg Pressure</h3>
                  <p>{summary.avg_pressure}</p>
                </div>
                <div className="card">
                  <h3>Avg Temperature</h3>
                  <p>{summary.avg_temperature}</p>
                </div>
              </div>
              <div style={{display: 'flex', gap: '10px', marginTop: '20px'}}>
                <button onClick={downloadPDF} className="pdf-btn">
                  📄 Download PDF Report
                </button>
                <button onClick={downloadExcel} className="excel-btn">
                  📊 Download Excel
                </button>
              </div>
            </section>

            <section className="charts-section">
              <h2>Visualizations</h2>
              <div className="charts-container">
                {pieChartData && (
                  <div className="chart">
                    <h3>Equipment Type Distribution</h3>
                    <Pie data={pieChartData} />
                  </div>
                )}
                {barChartData && (
                  <div className="chart">
                    <h3>Average Parameters</h3>
                    <Bar data={barChartData} />
                  </div>
                )}
              </div>
            </section>

            <section className="equipment-table">
              <h2>Equipment List</h2>
              <input 
                type="text" 
                placeholder="🔍 Search equipment by name or type..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-box"
              />
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Equipment Name</th>
                      <th>Type</th>
                      <th>Flowrate</th>
                      <th>Pressure</th>
                      <th>Temperature</th>
                    </tr>
                  </thead>
                  <tbody>
                    {equipmentList
                      .filter(eq => 
                        eq.equipment_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        eq.equipment_type.toLowerCase().includes(searchTerm.toLowerCase())
                      )
                      .map((equipment) => (
                        <tr key={equipment.id}>
                          <td>{equipment.equipment_name}</td>
                          <td>{equipment.equipment_type}</td>
                          <td>{equipment.flowrate}</td>
                          <td>{equipment.pressure}</td>
                          <td>{equipment.temperature}</td>
                        </tr>
                      ))
                    }
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
