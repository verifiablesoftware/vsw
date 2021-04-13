#!/bin/bash

docker run \
 --name ubuntu \
 -e HOST_IP=$(ifconfig en0 | awk ‘/ *inet /{print $2}’) \
 -v /home/ubuntu/felix:/workspace \
 --network host -t -i \
 ubuntu:bionic /bin/bash

#cat /etc/lsb-release
apt-get update
apt install python3-pip
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
apt-get install software-properties-common
add-apt-repository "deb https://repo.sovrin.org/sdk/deb bionic stable"
apt-get install -y libindy
pip3 install vsw