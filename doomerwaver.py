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


    try:
      sl = download(yturl[0].decode('utf-8'))
      of = doomify(sl)
      doom = open(of, 'rb')
      resp = doom.read()
      start_response('200 OK', [('Content-Type','audio/x-wav'), ('Content-Disposition','attachment'), ('Content-Length', str(len(resp)))])
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
      filename = ytdl.prepare_filename(info)
      return filename[:filename.find('.', -6)] + '.wav'

def doomify(sf):
  noise = 0.2
  wet = 1 - noise
  speed = 0.8

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
  
        vinbuf = vinyl.readframes(out.getframerate() * 3 // 2)
        out.writeframes(vinbuf)
        wavfs = wav.getsampwidth() * wav.getnchannels()
  
        while True:
          buf = wav.readframes(1024)
          if len(buf) <= 0:
            break
          vinbuf = vinyl.readframes(len(buf) // wavfs)
          if len(vinbuf) < len(buf):
            vinyl.rewind()
            vinbuf = vinyl.readframes(len(buf) // wavfs)
  
          a = np.frombuffer(buf, dtype='i2') * wet
          b = np.frombuffer(vinbuf, dtype='i2') * noise
  
          mod = a + b
  
          out.writeframes(mod.astype('i2').tobytes())

  return of
  

def main():
  if len(sys.argv) != 2:
    print('Expected a youtube url argument: e.g. ./doomify "http://..."')
    exit()

  sl = sys.argv[1]
  sf = download(sl)
  of = doomify(sf)
  os.system('open \"%s\"' % of)
        
if __name__ == '__main__':
  main()
