#!/usr/bin/env python3

import wave
import numpy as np
import youtube_dl
import sys
import os

def printinfo(name, wav):
  print(name)
  print('Compression:', wav.getcompname())
  print('Framerate:', wav.getframerate())
  print('# Frames:', wav.getnframes())
  print('# Channels:', wav.getnchannels())
  print('Sample Width:', wav.getsampwidth())

def download(link):
    print("Downloading", link)
    opts = {
        'format': 'bestaudio/best',
        'forcefilename': True,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }]
    }
    with youtube_dl.YoutubeDL(opts) as ytdl:
      info = ytdl.extract_info(link, download=True)
      return ytdl.prepare_filename(info)[:-5] + '.wav'


def main():
  if len(sys.argv) != 2:
    print('Expected a youtube url argument')
    exit()

  noise = 0.2
  wet = 1 - noise
  speed = 0.8

  nf = 'vinyl.wav'
  of = 'testout.wav'
  sl = sys.argv[1]
  sf = download(sl)
  with wave.open(sf, 'rb') as wav, wave.open(nf, 'rb') as vinyl:
    with wave.open(of, 'wb') as out:
      out.setparams(wav.getparams())
      out.setframerate(wav.getframerate() * speed)

      printinfo('Input Audio', wav)
      printinfo('Vinyl Sample', vinyl)
      printinfo('Output Audio', out)

      vinbuf = vinyl.readframes(out.getframerate() * 3 // 2)
      out.writeframes(vinbuf)
      vinbuf = None

      INT16_MIN = np.iinfo(np.int16).min
      INT16_MAX = np.iinfo(np.int16).max
      def mix(a, b):
        return (a + b) - ((a * b)/INT16_MIN) if a < 0 and b < 0  else ( (a + b) - ((a * b)/INT16_MAX) if a > 0 and b > 0 else a + b)
      mv = np.vectorize(mix)
        
      while True:
        buf = wav.readframes(1024)
        if len(buf) <= 0:
          break
        vinbuf = vinyl.readframes(len(buf) // 4)
        if len(vinbuf) < len(buf):
          vinyl.rewind()
          vinbuf = vinyl.readframes(len(buf) // 4)

        a = np.frombuffer(buf, dtype='i2') * wet
        b = np.frombuffer(vinbuf, dtype='i2') * noise

        
        #mod = mv(a, b)
        mod = a + b

        out.writeframes(mod.astype('i2').tobytes())
      os.system('open testout.wav')
        
if __name__ == '__main__':
  main()
