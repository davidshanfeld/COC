import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LiveDocument from './components/LiveDocument';
import './App.css';



function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />}>
            <Route index element={<Home />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
