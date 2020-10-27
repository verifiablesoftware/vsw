FROM node:15.0.1-alpine3.10

LABEL maintainer=yeak2001@gmail.com

ARG homeDir=/root
ARG user=vsw-repo
ARG appDir=/root/vsw-repo

ENV PORT 8000
ENV agent_home=/root/agent

RUN mkdir $appDir
RUN mkdir $agent_home

COPY ./app/ $appDir/
#COPY ../../aries-cloudagent-python/ $agent_home/

RUN apk add python3 && apk add py3-pip

WORKDIR $appDir
EXPOSE $PORT
RUN npm i

#ENTRYPOINT ["bash", "-c"]
CMD node app.js