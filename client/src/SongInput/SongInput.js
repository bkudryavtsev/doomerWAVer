import React, { useEffect, useState } from 'react';

import './SongInput.css';

const WSS_URL = 'ws://localhost:8080';

function SongInput(props) {
  const [data, setData] = useState({ status: 'ready' });
  const [ytUrl, setYtUrl] = useState('');

  let ws = null;

  useEffect(() => {
    return () => {
      ws?.close();
    }
  }, []);

  useEffect(() => {
    if (data) {
      console.log('Data: ', data);

      if (data.progress) {
        props.onProgress(calcProgress(data.progress));
      }

      if (data.status === 'done') {
          props.onResult(data);
      } else if (data.status === 'error') {
        props.onError(data);
      }
    }
  }, [data]);

  const calcProgress = p => {
    const dist = {
      downloading: 40, 
      processing: 40,
      uploading: 20
    };

    return Math.round(p.downloading * dist.downloading 
      + p.processing * dist.processing 
      + p.uploading * dist.uploading);
  };

  const generate = () => {
    if (ws?.readyState < 2) {
      return;
    }

    props.onRequest();
    props.onProgress(1);

    ws = new WebSocket(WSS_URL);

    ws.onopen = function() {
      const req = { ytUrl };
      ws.send(JSON.stringify(req));
      setData({ status: 'requested' });
    };

    ws.onmessage = function(e) {
      setData(JSON.parse(e.data));
    };

    ws.onclose = function() {
      setData({ status: 'ready' });
    }
  };

  return (
    <div className="SongInput">
      <input 
        type="text" 
        placeholder="Youtube URL" 
        disabled={data.status !== 'ready'}
        onChange={event => setYtUrl(event.target.value)}
        value={ytUrl} />
      <button 
        onClick={generate} 
        disabled={data.status !== 'ready'}>
          Generate
      </button>
    </div>
  );
};

export default SongInput;
