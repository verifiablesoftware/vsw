FROM ubuntu:18.04

WORKDIR /root

ENV DEBIAN_FRONTEND=noninteractive
ENV PORT=7062
ENV HTTP_PORT=7060
ENV ADMIN_PORT=7061
ENV WEBHOOK_PORT=7062
ENV EXTERNAL_HOST="3.141.51.96"

ARG VSW_VERSION

RUN apt update
RUN apt install -y python3-pip twine
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install python-daemon
RUN pip3 install vsw==${VSW_VERSION}
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
RUN apt update
RUN apt-get install -y software-properties-common
RUN add-apt-repository "deb https://repo.sovrin.org/sdk/deb bionic stable"
RUN apt update
RUN apt install -y libindy
RUN apt install -y curl 
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt install -y nodejs 
RUN apt install -y wget
RUN apt install -y unzip
RUN apt install -y jq
RUN apt install -y net-tools

RUN mkdir -p /usr/local/lib/python3.6/dist-packages/logs

COPY . /root/tests
