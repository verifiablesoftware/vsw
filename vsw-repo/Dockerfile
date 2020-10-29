FROM verifiablesoftware/aries-cloudagent-python:latest

ENV PORT=8000
EXPOSE $PORT
USER root
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
  apt-get install nodejs -y

COPY ./app/ ./
RUN npm i

HEALTHCHECK --interval=1m --timeout=3s \
  CMD curl \
      --fail \
      http://localhost:$PORT/health_check || \
      exit 1

CMD node app.js
