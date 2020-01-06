```
                                           ___                    
    |                               |   | |   | |  /              
   -|  -     -    |- -   -    |-    | + | |-+-| | +    -    |-    
  | | | |   | |   | | | |/    |     |/ \| |   | |/    |/    |     
   -   -     -           --                            --         
                                                                  



This is the source code of the doomerWAVer site.

It consists of two parts:
- The server portion; written in Python for use with uWSGI
- The frontend portion; written in React.js


Installation (server)
  Install instructions are rough since I doubt anyone will actually want to
  follow them (other than myself at a later time). Exercise common sense and
  google any issues preventing builds and whatnot.

  Steps:
  - install python3 and pip3
  - install uwsgi from pip3 and figure out where the hell it put the binary
  - clone this git repository somewhere 
  - (recommended for development) install virtualenv with pip3 and run
      virtualenv doomer && source doomer/bin/activate
    in the root of this repo
  - try to run "pip3 install -r requirements.txt"
  - it will fail.
  - install ffmpeg and ffmpeg-related stuff through your package manager
  - once requirements.txt install succeeds, run 
      ./start.sh             : for deployment configuration
      ./test.sh              : for development configuration (*)
      ./doomerwaver.py [url] : for one-shot test of the doomerwaver (*)

      (*) = requires virtualenv step described above
  - development configuration attaches server to port 8080 
  - deployment configuration attaches server to port 80 
  - SSL (https) not currently supported



Server architecture considerations
  Since I want this service to be free for users, I have to make do with an 
  ec2.tiny (free) instance on AWS. This means the service is rather limited in 
  throughput. The server is also highly limited in memory and disk space, so
  resampling is done by the individual frame of audio as it is being streamed
  from YouTube and to the end user simultaneously.
```
