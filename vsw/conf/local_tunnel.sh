#!/bin/bash
if which node > /dev/null
  then
      echo "node is installed."
  else
     echo "Sorry, you have not installed Nodejs, please go to https://nodejs.org/en/ to install it firstly."
     exit 0
fi
cd ~
if [ ! -d ~/localtunnel-master ]; then
    if [ ! -f ~/master.zip ]; then
      echo "Downloading localtunnel client source code"
      wget https://github.com/localtunnel/localtunnel/archive/master.zip
    fi
    echo "Unzip client source code"
    unzip master.zip
    cd ~/localtunnel-master
    npm install -g localtunnel
fi
cd ~/localtunnel-master
lt --port $1
echo "started localtunnel."