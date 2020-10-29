FROM verifiablesoftware/aries-cloudagent-python:latest

ENV PORT=8000

COPY ./app/ ./

EXPOSE $PORT
USER root
RUN apt-get update && apt-get install nodejs -y && apt-get install npm -y

RUN npm i

HEALTHCHECK --interval=1m --timeout=3s \
  CMD curl \
      --fail \
      http://localhost:$PORT/health_check || \
      exit 1

CMD node app.js
