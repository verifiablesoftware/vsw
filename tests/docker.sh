#!/bin/bash

docker run \
 --name ubuntu \
 -e HOST_IP=$(ifconfig en0 | awk ‘/ *inet /{print $2}’) \
 -v /var/folders/:/workspace \
 -t -i -p 8020:8020 -p 8021:8021 -p 8022:8022 \
 ubuntu:bionic /bin/bash

#cat /etc/lsb-release
apt-get update
apt install python3-pip
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
apt-get install software-properties-common
add-apt-repository "deb https://repo.sovrin.org/sdk/deb bionic stable"
apt-get install -y libindy
pip3 install vsw