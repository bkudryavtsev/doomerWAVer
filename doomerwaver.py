#!doomer/bin/python3

from cgi import parse_qs
import numpy as np
import sys
import os
import pafy
import wave
import av
from unidecode import unidecode


#GET_dir = ''
GET_dir = 'client/dist'
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
        start_response('400 BAD REQUEST', [
        ('Access-Control-Allow-Origin', '*'),
        ('Content-Type','text/plain')])
        return [b'POST request must have a yturl paramter containing the Youtube url']
      else:
        yturl = yturl[0].decode('utf-8')

      # Request good. Attempt to process video
      video = find_video(yturl)
      if video is None:
        start_response('400 BAD REQUEST', [
        ('Access-Control-Allow-Origin', '*'),
        ('Content-Type','text/plain')])
        return [b'Youtube link was not valid']

      astream = video.getbestaudio(preftype="webm")
      print('Found audio stream', astream)

      stream = stream_doom(astream.url)
      start_response('200 OK', [
        ('Content-Type','audio/mpeg'), 
        ('Content-Disposition','attachment; filename=doomer_%s.mp3' % unidecode(video.title)), 
        #('Content-Length', str(len(resp))), 
        ('Access-Control-Expose-Headers', '*'),
        ('Access-Control-Allow-Origin', '*')
        ]
      )
      #env['wsgi.file_wrapper'](doom, 32768)
      for chunk in stream:
        yield chunk
      
    elif method == 'GET':
      # Fetching the frontend
      url = env.get('PATH_INFO', '/')
      url = url.lstrip('/')
      if url == '':
        url = 'index.html'

      path = os.path.join(GET_dir, url)
      print('requesting:', url, 'Returning:',  path)

      try:
        with open(path, 'rb') as i:
          data = i.read()

          filetype = 'text/plain'
          if url.endswith('.html'):
            filetype = 'text/html'
          elif url.endswith('.js'):
            filetype = 'text/javascript'
          elif url.endswith('.css'):
            filetype = 'text/css'
          elif url.endswith('.jpeg') or url.endswith('.jpg'):
            filetype = 'image/jpeg'
          elif url.endswith('.png'):
            filetype = 'image/png'

          start_response('200 OK', [
          ('Access-Control-Allow-Origin', '*'),
          ('Content-Type',filetype)])

          yield data
      except Exception as e:
        start_response('404 Not Found', [
        ('Access-Control-Allow-Origin', '*'),
        ('Content-Type','text/html')])
        print(e)
        return [b'404. That file does not exist here']

    else:
      start_response('405 Method Not Allowed', [
      ('Access-Control-Allow-Origin', '*'),
      ('Content-Type','text/plain')])
      return [b'405. Request type not supported']
    
  except Exception as e:
    start_response('500 Internal Server Error', [
    ('Access-Control-Allow-Origin', '*'),
    ('Content-Type','text/plain')])
    print(e)
    return [str(e).encode('utf-8')]

  return [b"Something went incredibly wrong"]


def find_video(yturl: str):
  try:
    video = pafy.new(yturl)
    return video
  except:
    return None

def moving_average(a, n=3):
  ret = np.cumsum(a, dtype=float)
  ret[n:] = ret[n:] - ret[:-n]
  return ret[n - 1:] / n

def stream_doom(yturl: str, speed=None, noise=None):
  in_file = av.open(yturl, options={'rtsp_transport': 'tcp'})
  in_stream = in_file.streams.audio[0]
  in_codec = in_stream.codec_context

  out_codec = av.CodecContext.create('mp3', 'w')
  out_codec.rate = in_codec.rate 
  out_codec.channels = in_codec.channels 
  out_codec.format = in_codec.format 


  resampler = av.AudioResampler(
      format=av.AudioFormat('s16').packed,
      layout=in_codec.layout,
      rate=in_codec.rate * 1.4 if speed is None else 1 / speed,
  )

  if in_codec.channels == 2:
    nf = 'vinyl.wav'
  elif in_codec.channels == 1:
    nf = 'vinylmono.wav'
  else:
    exit(1)

  noise = noise or 0.1
  wet = 1 - noise

  with wave.open(nf, 'rb') as vinyl:
    vinbuf = vinyl.readframes(int(out_codec.rate * 1.5))
    b = np.frombuffer(vinbuf, dtype='i2').reshape((1, -1))
    newframe = av.audio.frame.AudioFrame.from_ndarray(b, format='s16', layout=in_codec.layout.name)
    newframe.rate = out_codec.rate
    for p in out_codec.encode(newframe):
      yield p.to_bytes()

    for packet in in_file.demux(in_stream):
      for frame in packet.decode():
        frame.pts = None
        buf = resampler.resample(frame).to_ndarray()[0]
        # reading in a frame of the vinyl
        vinbuf = vinyl.readframes(len(buf) // in_codec.channels)
        if len(vinbuf) < len(buf) * in_codec.channels:
          vinyl.rewind()
          vinbuf = vinyl.readframes(len(buf) // in_codec.channels)
        a = buf * wet
        b = np.frombuffer(vinbuf, dtype='i2') * noise
        mod = moving_average(a + b, n=7).astype('i2').reshape((1, -1))
        
        newframe = av.audio.frame.AudioFrame.from_ndarray(mod, format='s16', layout=in_codec.layout.name)
        newframe.rate = out_codec.rate
        for p in out_codec.encode(newframe):
          yield p.to_bytes()

    for p in out_codec.encode(newframe):
      yield p.to_bytes()

  in_file.close()



def main():
  """A quick way to test the program without bringing up any servers"""
  if len(sys.argv) < 2: sys.exit('Expected a youtube url argument: e.g. ./doomify "http://..."')
  speed = float(sys.argv[2]) if len(sys.argv) >= 3 else None
  video = find_video(sys.argv[1])
  astream = video.getbestaudio(preftype="webm")
  print('Found audio stream', astream)

  with open('output.mp3', 'wb') as out:
    for chunk in stream_doom(astream.url, speed=speed):
      out.write(chunk)
        
if __name__ == '__main__':
  main()
