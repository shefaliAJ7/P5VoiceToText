import React from './../../node_modules/react';
import './../styles/App.css';
import './../../node_modules/bootstrap/dist/css/bootstrap.min.css';
import History from '../containers/History';

function Thirdpage() {
  return (
    <div className='Thirdpage' id='hist'>
      <History />
    </div>
  );
}

export default Thirdpage;
