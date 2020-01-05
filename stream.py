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
print('video:', dir(video))
stream = video.getbestaudio(preftype="webm")
print('stream:', dir(stream))

print('Found audio stream', stream)
container = av.open(stream.url, options={'rtsp_transport': 'tcp'})
audio = container.streams.audio[0]

print(dir(audio))
print(audio.codec_context)
print(audio.metadata)
with wave.open('output.wav', 'wb') as out:
  #out.setparams(wav.getparams())
  out.setnchannels(1)
  out.setsampwidth(2)
  out.setframerate(stream.rawbitrate )

  for frame in container.decode(audio):
    out.writeframes(frame.to_ndarray())
