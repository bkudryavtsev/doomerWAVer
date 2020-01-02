import React, { useState } from 'react';
import SongInput from '../SongInput/SongInput';

import './App.css';

const App = () => {
  const [errText, setErrText] = useState();

  const onSongInputError = err => {
    setErrText(err);
  }

  return (
    <div className="App">
      <div className="content">
        <h1 className="title">doomerWAVer</h1>
        <div className="song-input-container">
          <SongInput onError={onSongInputError} />
          {errText && <p className="song-input-err">{errText}</p>}
        </div>
        <h2 className="subtitle">Generate your favorite doomerwave for those long, sleepless nights.</h2>
      </div>
    </div>
  );
};

export default App;