import { WebSocketServer } from 'ws';
import { promises as fs } from 'fs';
import ytdl from 'ytdl-core';
import ffmpeg from 'fluent-ffmpeg';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const STATUS = {
  error: 'error',
  downloading: 'downloading',
  processing: 'processing',
  uploading: 'uploading',
  done: 'done'
};

const VINYL_PATH = path.resolve(__dirname, 'effects/vinyl.wav');
const DATA_DIR = path.resolve(__dirname, 'data');

const MAX_VIDEO_DURATION = 600;
const TEMPO = 0.85;
const LOWPASS_THRESH = 1000; // Hz
const DELAY = 2; // seconds

const wss = new WebSocketServer({ port: 8080 });

function clamp(n, min, max) {
  return Math.min(Math.max(n, min), max);
}

async function getFile(path) {
  let file;

  try {
    file = await fs.readFile(path);
  } catch (err) {
    return null;
  }

  return file;
}

function calcProgress(targetSize, totalDuration) {
  return parseFloat((targetSize / ((totalDuration * 128) / 8)).toFixed(2));
}

async function deleteFile(filePath) {
  try {
    await fs.unlink(filePath);
  } catch (err) {
    console.error(`Unable to delete file ${filePath}`, err);
  }
}

function downloadAudio(videoId, duration, filePath, onProgress, onEnd, onError) {
  const audio = ytdl(videoId, { quality: 'highestaudio' });

  return ffmpeg(audio)
    .audioBitrate(128)
    .save(filePath)
    .on('progress', p => onProgress(clamp(calcProgress(p.targetSize, duration), 0, 1)))
    .on('end', () => onEnd())
    .on('error', err => onError(err));
}

function preProcessAudio(inFilePath, outFilePath, duration, onProgress, onEnd, onError) {
  return ffmpeg(inFilePath) 
    .audioFilter(`adelay=${DELAY}s:all=true`)
    .audioFilter(`atempo=${TEMPO}`)
    .audioFilter(`lowpass=f=${LOWPASS_THRESH}`)
    .save(outFilePath)
    .on('progress', p => onProgress(clamp(0.5 * calcProgress(p.targetSize, duration), 0, 0.5)))
    .on('end', () => onEnd())
    .on('error', err => onError(err));
}

function processAudio(inFilePath, outFilePath, duration, onProgress, onEnd, onError) {
  return ffmpeg(inFilePath)
    .input(VINYL_PATH)
    .inputOption('-stream_loop -1')
    .complexFilter([
      {
        filter: 'amix', options: { inputs : 2, duration : 'first', weights: '3 1' }
      }
    ])
    .save(outFilePath)
    .on('progress', p => onProgress(clamp(0.5 + calcProgress(p.targetSize, duration), 0.5, 1)))
    .on('end', () => onEnd())
    .on('error', err => onError(err));
}

wss.on('connection', ws => {
  let ffmpegCmd;

  ws.on('message', async d => {
    const { ytUrl } = JSON.parse(d);

    console.log('received: %s', d);

    if (!ytUrl || !ytUrl?.length || !ytdl.validateURL(ytUrl)) {
      ws.send(JSON.stringify({ status: STATUS.error, message: 'Not a valid YouTube URL' })); 
      ws.close();
      return;
    }

    let videoId;
    let videoInfo;
    let videoDuration;

    try {
      videoId = ytdl.getVideoID(ytUrl);
      videoInfo = await ytdl.getBasicInfo(videoId);
      videoDuration = videoInfo.videoDetails?.lengthSeconds;
    } catch {
      ws.send(JSON.stringify({ status: STATUS.error, message: 'Unable to get video information from URL' })); 
      ws.close();
      return;
    }
    
    if (videoDuration > MAX_VIDEO_DURATION) {
      ws.send(JSON.stringify({ status: STATUS.error, message: 'Video cannot be longer than 10 minutes' }));
      ws.close();
      return;
    }

    const filePath = `${DATA_DIR}/${videoId}.mp3`;
    const dlFilePath = `${DATA_DIR}/_${videoId}.mp3`;
    const tempFilePath = `${DATA_DIR}/~${videoId}.mp3`; 

    const onError = (err, msg) => {
      ws.send(JSON.stringify({ status: STATUS.error, message: msg }));
      ws.close();
      console.error(err);
    };

    const sendProgress = (status, downloading, processing, uploading) => {
      ws.send(JSON.stringify({
        status: status,
        progress: {
          downloading,
          processing,
          uploading
        }
      }));   
    };

    const sendFile = file => {
      sendProgress(STATUS.uploading, 1, 1, 0.5);
      ws.send(JSON.stringify({
        status: 'done',
        audio: 'data:audio/mp3;base64,' + file.toString('base64'),
        info: {
          title: videoInfo.videoDetails.title
        },
        progress: {
          downloading: 1,
          processing: 1,
          uploading: 1
        }
      }));

      ws.close();
    };

    let file = await getFile(filePath);

    if (file) {
      sendFile(file); 
      return;
    }

    ffmpegCmd = downloadAudio(videoId, videoDuration, dlFilePath, p => {
      sendProgress(STATUS.downloading, p, 0, 0);
    }, () => {
      sendProgress(STATUS.downloading, 1, 0, 0);

      ffmpegCmd = preProcessAudio(dlFilePath, tempFilePath, videoDuration, p => {
        sendProgress(STATUS.processing, 1, p, 0);
      }, async () => {
        await deleteFile(dlFilePath);
        sendProgress(STATUS.processing, 1, 0.5, 0);
        
        ffmpegCmd = processAudio(tempFilePath, filePath, videoDuration, p => {
          sendProgress(STATUS.processing, 1, p, 0);
        }, async () => {
          sendProgress(STATUS.processing, 1, 1, 0);

          await deleteFile(tempFilePath);

          file = await getFile(filePath);
          sendFile(file); 
        }, err => onError(err, 'Error processing audio'));
      }, err => onError(err, 'Error processing audio'));
    }, err => onError(err, 'Error downloading video'));
  });

  ws.on('close', () => {
    ffmpegCmd?.kill();
  });
});
