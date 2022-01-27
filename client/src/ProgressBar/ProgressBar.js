import React, { useState } from 'react';

import './ProgressBar.css';

function ProgressBar(props) {
  const { width, error, message } = props;

  return(
    <div className={`meter${width < 100 && !error ? ' animate' : ''}`}>
      {error ? <>
        <p>{error}</p>
        <span style={{ width: '100%', backgroundColor: '#606060' }}></span>
      </> : <>
        <p>{width}%</p>
        <span style={{ width: `${width}%` }}></span>
      </>}
      
    </div>
  );
}

export default ProgressBar;