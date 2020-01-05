import pafy
import sys
from urllib3 import request
import av
import wave

if len(sys.argv) < 2:
  print('Expected url')
  exit()

url = sys.argv[1]
video = pafy.new(url)
astream = video.getbestaudio(preftype="webm")

print('Found audio stream', astream)
container = av.open(astream.url, format='webm', options={'rtsp_transport': 'tcp'})
stream = container.streams.audio[0]

def decode_iter():
  for pi, packet in enumerate(container.demux(stream)):
    for fi, frame in enumerate(packet.decode()):
      yield pi, fi, frame

resampler = av.AudioResampler(
    format=av.AudioFormat('s16').packed,
    layout='stereo',
    rate=astream.rawbitrate // 3,
)

with wave.open('output.wav', 'wb') as out:
  pi, fi, frame = next(decode_iter())
  print(dir(frame))
  print(frame.layout)
  print(frame.format)
  #out.setparams(wav.getparams())
  out.setnchannels(2)
  out.setsampwidth(2)
  out.setframerate(astream.rawbitrate // 4)


  for pi, fi, frame in decode_iter():
    frame.pts = None
    out.writeframes(resampler.resample(frame).to_ndarray().tobytes())
