import pafy
import sys
from urllib3 import request
import av

if len(sys.argv) < 2:
  print('Expected url')
  exit()

url = sys.argv[1]
video = pafy.new(url)
astream = video.getbestaudio(preftype="webm")
print('Found audio stream', astream)

in_file = av.open(astream.url, format='webm', options={'rtsp_transport': 'tcp'})
in_stream = in_file.streams.audio[0]
in_codec = in_stream.codec_context

out_codec = av.CodecContext.create('mp3', 'w')
out_codec.rate = in_codec.rate 
out_codec.channels = in_codec.channels 
out_codec.format = in_codec.format 


resampler = av.AudioResampler(
    format=av.AudioFormat('s16').packed,
    layout=in_codec.layout,
    rate=in_codec.rate * 1.3,
)

with open('output.mp3', 'wb') as out:
  for packet in in_file.demux(in_stream):
    for frame in packet.decode():
      frame.pts = None
      array = resampler.resample(frame).to_ndarray()
      newframe = av.audio.frame.AudioFrame.from_ndarray(array, format='s16', layout='stereo')
      newframe.rate = in_codec.rate
      for p in out_codec.encode(newframe):
        out.write(p.to_bytes())
        #out_file.mux(packet)

  for p in out_codec.encode(newframe):
    out.write(p.to_bytes())

  in_file.close()

