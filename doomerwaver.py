#!/usr/bin/env python3

from cgi import parse_qs
import wave
import pydub
import numpy as np
import youtube_dl
import sys
import os
from unidecode import unidecode


def application(env, start_response):
  """Main wsgi entry point"""

  method = env['REQUEST_METHOD']

  try:
    if method == 'POST':
      # Process file
      request_body_size = int(env.get('CONTENT_LENGTH', 0))
      request_body = env['wsgi.input'].read(request_body_size)
      d = parse_qs(request_body)

      yturl = d.get(b'yturl', None)
      if not yturl:
        start_response('400 BAD REQUEST', [('Content-Type','text/plain')])
        return [b'POST request must have a yturl paramter containing the Youtube url']
      else:
        yturl = yturl[0].decode('utf-8')

      # Request good. Attempt to process video
      of = cached_doom(yturl)
      doom = open(of, 'rb')
      resp = doom.read()
      start_response('200 OK', [
        ('Content-Type','audio/x-wav'), 
        ('Content-Disposition','attachment; filename=' + unidecode(of)), 
        ('Content-Length', str(len(resp))), 
        ('Access-Control-Allow-Origin', '*')
        ]
      )
      return [resp]
      
    elif method == 'GET':
      # Fetching the frontend
      url = env.get('PATH_INFO', '/')

      if url in ['index.html', '/', '']:
        with open('index.html', 'rb') as i:
          data = i.read()
          start_response('200 OK', [('Content-Type','text/html')])
          return [data]
      else:
        start_response('404 Not Found', [('Content-Type','text/html')])
        return [b'404. That file does not exist here']

    else:
      start_response('405 Method Not Allowed', [('Content-Type','text/plain')])
      return [b'405. Request type not supported']
    
  except Exception as e:
    start_response('500 Internal Server Error', [('Content-Type','text/plain')])
    print(e)
    return [str(e).encode('utf-8')]

  return [b"Something went incredibly wrong"]

cache = {}
def cached_doom(yturl: str) -> str:
  """Check if video has been processed, if yes, return, else process
  Args:
    yturl (str): url of the youtube video
  Returns:
    str: the filename of the processed audio
  """
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
  

def printinfo(label: str, wav: wave.Wave_read, outfile=sys.stdout):
  """Print info about a wav file for logging purposes
  Args:
    label (str): The human-readable name of the file being shown
    wav (Wave_read): The open wave object
    outfile (file, optional): The output stream for the info. Defaults to stdout
  """
  print(label, file=outfile)
  print('Compression:', wav.getcompname(), file=outfile)
  print('Framerate:', wav.getframerate(), file=outfile)
  print('# Frames:', wav.getnframes(), file=outfile)
  print('# Channels:', wav.getnchannels(), file=outfile)
  print('Sample Width:', wav.getsampwidth(), file=outfile)

def download(link: str):
  """Download the audio from the youtube url and convert to mp3
  Args:
    link (str): The url of the youtube video
  """
  print("Downloading", link)
  maxfilesize = 20000000 # 20MB
  opts = {
    'format': 'bestaudio/best',
    'forcefilename': True,
    'quiet': True,
    'noplaylist': True,
    'max_downloads': 1,
    'max_filesize': maxfilesize,
    'postprocessors': [{
      'key': 'FFmpegExtractAudio',
      'preferredcodec': 'wav',
      'preferredquality': '192',
    }]
  }
  with youtube_dl.YoutubeDL(opts) as ytdl:
    info = ytdl.extract_info(link, download=False)
    if info['filesize'] > maxfilesize:
      raise Exception('Sorry brother, I can\'t handle a file this size') 
    ytdl.download([link])
    filename = ytdl.prepare_filename(info)
    return filename[:filename.find('.', -6)] + '.wav'

def moving_average(a, n=3):
  ret = np.cumsum(a, dtype=float)
  ret[n:] = ret[n:] - ret[:-n]
  return ret[n - 1:] / n

def doomify(sf: str, verbose=False) -> str:
  """Takes a wave file and returns a doomified mp3
  Args:
    sf (str): Source file name
    verbose (bool, optional): print file info
  Returns:
    str: Output file name (mp3)
  """
  noise = 0.1
  wet = 1 - noise
  speed = 0.74

  temp = 'doomer_' + sf
  of = 'doomer_%s.mp3' % sf[:-4] 
  with wave.open(sf, 'rb') as wav:
    inchannels = wav.getnchannels()
    if inchannels == 2:
      nf = 'vinyl.wav'
    elif inchannels == 1:
      nf = 'vinylmono.wav'
    else:
      exit(1)

    with wave.open(nf, 'rb') as vinyl, wave.open(temp, 'wb') as out:
      out.setparams(wav.getparams())
      out.setframerate(wav.getframerate() * speed)

      if verbose:
        printinfo('Input Audio', wav)
        printinfo('Vinyl Sample', vinyl)
        printinfo('Output Audio', out)

      vinbuf = np.frombuffer(vinyl.readframes(out.getframerate() * 3 // 2), dtype='i2') * noise
      out.writeframes(vinbuf.astype('i2').tobytes())

      wavcns = wav.getnchannels() * 2

      while True:
        buf = wav.readframes(1024)
        if len(buf) <= 0:
          break
        vinbuf = vinyl.readframes(len(buf) // wavcns)
        if len(vinbuf) < len(buf):
          vinyl.rewind()
          vinbuf = vinyl.readframes(len(buf) // wavcns)
        a = np.frombuffer(buf, dtype='i2') * wet
        b = np.frombuffer(vinbuf, dtype='i2') * noise
        mod = moving_average(a + b, n=7)
        out.writeframes(mod.astype('i2').tobytes())

    pydub.AudioSegment.from_wav(temp).export(of, format='mp3')
    os.unlink(temp)
  print('Generated', of)
  return of
  

def main():
  """A quick way to test the program without bringing up any servers"""
  if len(sys.argv) != 2: sys.exit('Expected a youtube url argument: e.g. ./doomify "http://..."')
  os.system('open \"%s\"' % cached_doom(sys.argv[1]))
        
if __name__ == '__main__':
  main()
