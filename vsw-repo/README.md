
# VSW REPO

Node.js based repo controller



## USAGE

run docker

create DID

create invitation

## build image 
```
docker build -t vsw-repo .
```

## run container
```
 docker run -d --name vsw-repo -p 8000:8000 vsw-repo
```
or
```
 docker run -d --name vsw-repo -p 8000:8000 -p 8060:8060 -p 8061:8061 vsw-repo
```



or run from the shell script
```
chmod +x start.sh
./start.sh
```

