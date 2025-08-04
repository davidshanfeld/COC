import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LiveDocument from './components/LiveDocument';
import './App.css';



function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LiveDocument />} />
          <Route path="/live-document" element={<LiveDocument />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
