import React, { useState } from 'react';
import axios from 'axios';

import './SongInput.css';
import '../css/la-line-scale.css';

const MAX_DISPLAY_FILENAME_CHARS = 40;

const SongInput = props => {
  const [generating, setGenerating] = useState(false);
  const [ytUrl, setYtUrl] = useState('');
  const [file, setFile] = useState();
  const [filename, setFilename] = useState();

  const resetOnError = err => {
    setGenerating(false);
    setFile(undefined);
    setFilename(undefined);
    props.onError(err);
  }

  const isYouTubeUrl = url => {
    const regex = /^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    return regex.test(url);
  }
  
  const handleGenerate = event => {
    props.onError();

    if (!isYouTubeUrl(ytUrl)) {
      resetOnError('Please use a valid YouTube URL');
      return;
    }

    setGenerating(true);
    
    axios({
      url: '',
      method: 'POST',
      responseType: 'blob',
      data: `yturl=${ytUrl}`
    }).then(res => {
      if (res.status === 200) {
        setGenerating(false);

        const headers = res.headers;
        const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        let _filename = filenameRegex.exec(headers['content-disposition'])[0].replace('filename=', '');
        setFilename(_filename);

        if (_filename.length > MAX_DISPLAY_FILENAME_CHARS) {
          _filename = _filename.substring(0, MAX_DISPLAY_FILENAME_CHARS - 3) + '...';
        }
        
        const fileUrl = URL.createObjectURL(new Blob([res.data], { type: headers['content-type'] }));
        setFile(fileUrl);

        const timeoutId = setTimeout(() => {
          const successContent = document.querySelector('.success-content');
          successContent.innerHTML = `<p>Download ${_filename}</p>`;
          clearTimeout(timeoutId);
        }, 600);
      } else {
        console.log(res);
        resetOnError('An error occured');
      }
    }).catch(err => {
      console.log(err.response.statusText);
      resetOnError('An error occured');
    });
  };

  const downloadFile = event => {
    let element = document.createElement('a');
    element.setAttribute('href', file);
    element.setAttribute('download', filename);
  
    element.style.display = 'none';
    document.body.appendChild(element);
  
    element.click();
  
    document.body.removeChild(element);

    setYtUrl('');
    setFilename(undefined);
    setFile(undefined);
  }

  return (
    <div className="SongInput">
      <input 
        type="text" 
        placeholder="Youtube URL" 
        disabled={generating}
        onChange={event => setYtUrl(event.target.value)}
        value={ytUrl} />
      <button 
        onClick={handleGenerate} 
        disabled={generating}
        style={file ? { visibility: 'none' } : {}}>
        {!generating ? 
          'Generate' 
          : <div className="la-line-scale la-sm">
              <div></div>
              <div></div>
              <div></div>
              <div></div>
              <div></div>
            </div>}
      </button>
      {file &&
        <div className="success-anim">
          <div onClick={downloadFile} className="success-content"></div>
        </div>
      }
    </div>
  );
};

export default SongInput;
