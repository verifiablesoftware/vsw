#!/bin/bash
if which node > /dev/null
  then
      echo "node is installed."
  else
     echo "Sorry, you have not installed Nodejs, please go to https://nodejs.org/en/ to install it firstly."
     exit 0
fi
if [ ! -d ~/vsw_tools ]; then
  mkdir ~/vsw_tools
fi
if [ ! -d ~/vsw_tools/localtunnel-master ]; then
    cd ~/vsw_tools/
    if [ ! -f ~/vsw_tools/master.zip ]; then
      echo "Downloading localtunnel client source code"
      wget https://github.com/localtunnel/localtunnel/archive/master.zip
    fi
    echo "Unzip client source code"
    unzip -o master.zip
    cd ~/vsw_tools/localtunnel-master
    npm install -g localtunnel
    rm -rf ~/vsw_tools/master.zip
fi
cd ~/vsw_tools/localtunnel-master
npx localtunnel --port $1 --subdomain $2