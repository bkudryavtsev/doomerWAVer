import React, { useEffect, useState } from 'react';

import './SongInput.css';

const ws = new WebSocket('ws://localhost:8080');

function SongInput(props) {
  const [status, setStatus] = useState();
  const [ytUrl, setYtUrl] = useState('');

  useEffect(() => {
    ws.onmessage = function (e) {
      const data = JSON.parse(e.data);
      setStatus(data.status);

      console.log(data)

      if (data.status === 'done' && data.audio) {
        props.onResult(data);
      } else if (data.status === 'error') {
        props.onError(data);
      }
    };

    return function cleanup() {
      ws.close();
    }
  }, []);

  const create = () => {
    if (status === 'ready') {
      const req = { ytUrl };
      ws.send(JSON.stringify(req));
      setStatus('requested');
    }
  };

  return (
    <div className="SongInput">
      <input 
        type="text" 
        placeholder="Youtube URL" 
        disabled={false}
        onChange={event => setYtUrl(event.target.value)}
        value={ytUrl} />
      <button 
        onClick={create} 
        disabled={status !== 'ready'}>
          Generate
      </button>
    </div>
  );
};

export default SongInput;
