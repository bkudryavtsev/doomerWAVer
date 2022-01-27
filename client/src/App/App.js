import React, { useEffect, useState } from 'react';

import makeItRain from '../bg/rain';
import '../bg/rain.css';
import '../bg/bg.css';

import './App.css';

import SongInput from '../SongInput/SongInput';
import ProgressBar from '../ProgressBar/ProgressBar';

function App() {
  const [errText, setErrText] = useState();
  const [audio, setAudio] = useState();
  const [audioTitle, setAudioTitle] = useState();
  const [progress, setProgress] = useState(0);

  const onSongInputError = err => {
    setErrText(err.message);
  };

  const onSongInputResult = data => {
    setAudio(data.audio);
    setAudioTitle(data.info.title);
  };

  const onSongInputRequest = () => {
    setAudio(null);
    setAudioTitle(null);
    setErrText(null);
  };

  useEffect(() => {
    makeItRain();
  }, []);

  const download = (filename, data) => {
    const element = document.createElement('a');
    element.setAttribute('href', data);
    element.setAttribute('download', filename);
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  }

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
          <SongInput 
            onRequest={onSongInputRequest}
            onResult={onSongInputResult} 
            onError={onSongInputError} 
            onProgress={p => setProgress(p)}
            />
          {(errText || progress > 0) &&
            <ProgressBar width={progress} error={errText}></ProgressBar>
          }
        </div>
        {audio && <>
          <p className="audio-title">doomerwave - {audioTitle}</p>
          <div className="audio-container">
            <audio controls="controls" src={audio}></audio>
            <a className="download-button" onClick={e => download(`doomerwave - ${audioTitle}.mp3`, audio)}>&#11015;</a>
          </div>
        </>}
        <h2 className="subtitle">Generate your favorite doomerwave for those long, sleepless nights.</h2>
      </div>
    </div>
  );
}

export default App;
