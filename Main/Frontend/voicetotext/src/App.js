import React, { Component } from 'react';
import logo from './pchlogo.png';
import './App.css';


import Home from './Home';



class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">Voice to Text Pediatric IMIST-AMBO criteria</h1>


        </header>
        <Home/>
      </div>
      
      
    );
  }
}


export default App;
