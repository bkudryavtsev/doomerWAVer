#!/usr/bin/env python3

from cgi import parse_qs

def application(env, start_response):
  method = env['REQUEST_METHOD']

  if method == 'POST':
    try:
      request_body_size = int(env.get('CONTENT_LENGTH', 0))
    except (ValueError):
      request_body_size = 0

    request_body = env['wsgi.input'].read(request_body_size)
    d = parse_qs(request_body)
    print(d)

    yturl = d.get(b'yturl', None)
    if not yturl:
      print('yturl missing')
      start_response('400 BAD REQUEST', [('Content-Type','text/plain')])
      return[b'']
    else:
      yturl = yturl[0].decode('utf-8')


    try:
      of = cached_doom(yturl)
      doom = open(of, 'rb')
      resp = doom.read()
      start_response('200 OK', [('Content-Type','audio/x-wav'), ('Content-Disposition','attachment; filename=' + of), ('Content-Length', str(len(resp)))])
      return [resp]
    except Exception as e:
      print(e)
      start_response('500 INTERNAL SERVER ERROR', [('Content-Type','text/plain')])
    
  elif method == 'GET':
      with open('index.html', 'rb') as i:
        data = i.read()
        start_response('200 OK', [('Content-Type','text/html')])
        return(data)
        

  else:
    start_response('400 BAD REQUEST', [('Content-Type','text/plain')])
    
  return [b"kek"]

import wave
import pydub
import numpy as np
import youtube_dl
import sys
import os

cache = {}
def cached_doom(yturl):
  vid = yturl[yturl.find('=') + 1:]
  print(vid)
  cached = cache.get(vid, None)
  if cached:
    return cached
  else:
    sl = download(yturl)
    of = doomify(sl)
    os.unlink(sl)
    cache[vid] = of
    return of
  

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
      filename = ytdl.prepare_filename(info)
      return filename[:filename.find('.', -6)] + '.wav'

def moving_average(a, n=3) :
  ret = np.cumsum(a, dtype=float)
  ret[n:] = ret[n:] - ret[:-n]
  return ret[n - 1:] / n

def doomify(sf):
  noise = 0.15
  wet = 1 - noise
  speed = 0.74

  of = 'doomer_' + sf
  with wave.open(sf, 'rb') as wav:
    inchannels = wav.getnchannels()
    if inchannels == 2:
      nf = 'vinyl.wav'
    elif inchannels == 1:
      nf = 'vinylmono.wav'
    else:
      exit(1)

    with wave.open(nf, 'rb') as vinyl:
      with wave.open(of, 'wb') as out:
        out.setparams(wav.getparams())
        out.setframerate(wav.getframerate() * speed)
  
        printinfo('Input Audio', wav)
        printinfo('Vinyl Sample', vinyl)
        printinfo('Output Audio', out)
  
        vinbuf = np.frombuffer(vinyl.readframes(out.getframerate() * 3 // 2), dtype='i2') * noise
        out.writeframes(vinbuf.astype('i2').tobytes())

        wavcns = wav.getnchannels()
  
        while True:
          buf = wav.readframes(1024)
          if len(buf) <= 0:
            break
          a = moving_average(np.frombuffer(buf, dtype='i2') * wet, n=9)
          vinbuf = vinyl.readframes(len(a) // wavcns)
          if len(vinbuf) < len(a) * 2:
            vinyl.rewind()
            vinbuf = vinyl.readframes(len(a) // wavcns)
  
          b = np.frombuffer(vinbuf, dtype='i2') * noise
  
          mod = a + b
  
          out.writeframes(mod.astype('i2').tobytes())
        pydub.AudioSegment.from_wav(of).export(of + '.mp3', format='mp3')

  return of + '.mp3'
  

def main():
  if len(sys.argv) != 2:
    print('Expected a youtube url argument: e.g. ./doomify "http://..."')
    exit()

  sl = sys.argv[1]
  of = cached_doom(sl)
  os.system('open \"%s\"' % of)
        
if __name__ == '__main__':
  main()
