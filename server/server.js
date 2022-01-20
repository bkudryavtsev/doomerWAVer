import { WebSocketServer } from 'ws';
import { promises as fs } from 'fs';
import ytdl from 'ytdl-core';
import ffmpeg from 'fluent-ffmpeg';

const wss = new WebSocketServer({ port: 8080 });

const STATUS = {
  ready: 'ready',
  error: 'error',
  downloading: 'downloading',
  processing: 'processing',
  uploading: 'uploading',
  done: 'done'
};

const readyRes = JSON.stringify({ status: STATUS.ready });

wss.on('connection', ws => {
  ws.send(readyRes);

  ws.on('message', async d => {
    const { ytUrl } = JSON.parse(d);

    console.log('received: %s', d);

    if (ytUrl) {
      if (!ytdl.validateURL(ytUrl)) {
        ws.send(JSON.stringify({ status: STATUS.error, error: 'Not a valid YouTube URL' })); 
        ws.send(readyRes);
        return;
      }

      const videoId = ytdl.getVideoID(ytUrl);
      const videoInfo = await ytdl.getBasicInfo(videoId);
      const videoDuration = videoInfo.videoDetails?.lengthSeconds;
      
      if (videoDuration > 600) {
        ws.send(JSON.stringify({ status: STATUS.error, error: 'Video cannot be longer than 10 minutes' }));
        ws.send(readyRes);
      }

      const sendFile = file => {
        ws.send(JSON.stringify({
          status: 'done',
          audio: 'data:audio/mp3;base64,' + file.toString('base64') 
        }));
      }

      let fileExists;

      try {
        const file = await fs.readFile(`data/${videoId}.mp3`);
        fileExists = true;
        sendFile(file);
      } catch (err) {
        fileExists = false;
      }

      if (!fileExists) {
        const audio = ytdl(ytUrl, { quality: 'highestaudio' });

        ffmpeg(audio)
          .audioBitrate(128)
          .save(`data/${videoId}.mp3`)
          .on('progress', p => {
            ws.send(JSON.stringify({
              status: STATUS.downloading,
              progress: parseFloat((p.targetSize / ((videoDuration * 128) / 8) * 100).toFixed(2))
            }));
          }).on('end', async () => {
            ws.send(JSON.stringify({
              status: STATUS.downloading,
              progress: 100
            }));

            const file = await fs.readFile(`data/${videoId}.mp3`);
            sendFile(file);
          });
      }

      // ws.send(readyRes);
    }
  });
});
