#!/bin/sh

NAME=vsw-repo
echo "start ${NAME}" 

if [ !"$(docker ps -qq -f name=${NAME})" ]; then
    echo "container ${NAME} is running, delete it first"
    docker rm ${NAME} -f
fi

docker build -t ${NAME} .
docker run -d --name ${NAME} -p 8000:8000 ${NAME}