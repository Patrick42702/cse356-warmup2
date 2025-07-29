# Video Sharing Application

This is a scalable containerized application that I wrote to experiment with many different concepts, such as
* authentication via jwt
* video transcoding via ffmpeg from mp4 to mpeg-dash format
* microservice design via docker/docker-compose

## Todo

* Design a collaborative filtering algorithm that is reproducable at the region level, so
that it is scalable around the globe
* Deploy via kubernetes

## Env variables needed to run app:

These env files are needed in order to run the application via docker-compose:

### /auth/.env
| Key | Value |
| --- | --- |
| MONGO_URI | <Mongo db connection string, ex: mongodb://host.docker.internal:27017/>|

