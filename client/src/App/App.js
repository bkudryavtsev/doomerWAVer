import React, { useEffect, useState } from 'react';

import makeItRain from '../bg/rain';
import '../bg/rain.css';
import '../bg/bg.css';

import './App.css';

import SongInput from '../SongInput/SongInput';

function App() {
  const [errText, setErrText] = useState();
  const [audio, setAudio] = useState();

  const onSongInputError = err => {
    setErrText(err);
  }

  const onSongInputResult = data => {
    setAudio(data.audio);
  }

  useEffect(() => {
    makeItRain();
  }, []);

  return (
    <div className="App">
      <div className="bg">
        <div className="rain front-row"></div>
        <div className="rain back-row"></div>
        <div className="scanlines"></div>
        <div className="noise"></div>
        <div className="noise noise-moving"></div>
        <img className="doomer-img" src="/doomer.png" />
      </div>
      <div className="content">
        <h1 className="title">doomerWAVer</h1>
        <div className="song-input-container">
          <SongInput onResult={onSongInputResult} onError={onSongInputError} />
          {errText && <p className="song-input-err">{errText}</p>}
        </div>
        {audio && 
          <audio controls="controls" src={audio}></audio>
        }
        <h2 className="subtitle">Generate your favorite doomerwave for those long, sleepless nights.</h2>
      </div>
    </div>
  );
}

export default App;
