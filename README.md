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
| MONGO_DB | <DB name> |
| JWT_ALGORITHM | <EX: HS256> |
| SECRET_KEY | Secret key for jwt_algo |

### /transcoder/.env
| Key | Value |
| --- | --- |
| CELERY_BROKER_URL | redis://redis:6379/1 |
| CELERY_RESULT_BACKEND | redis://redis:6379/1 |
| S3_ENDPOINT | http://host.docker.internal:9000/ |
| S3_ACCESS_KEY | minioadmin |
| S3_SECRET_KEY | minioadmin |
| S3_BUCKET | video-bucket |
| MONGO_URI | mongodb://host.docker.internal:27017/ |
| MONGO_DB | video-app |
| TEMP_VIDEO_DIRECTORY | /app/temp/videos |
| PROCESSING | processing |
| PROCESSED | processed |

### /video/.env

| Key | Value |
| --- | --- |
| CELERY_BROKER_URL | redis://redis:6379/1 |
| S3_ENDPOINT | http://host.docker.internal:9000/ |
| S3_ACCESS_KEY | minioadmin |
| S3_SECRET_KEY | minioadmin |
| S3_BUCKET | video-bucket |
| MONGO_URI | mongodb://host.docker.internal:27017/ |
| MONGO_DB | video-app |
| SECRET_KEY | Same as auth |
| JWT_ALGORITHM | same as auth |

In order to run the app, you also need to create a video bucket inside of
minio. Go to the console in localhost:9000, use minioadmin for user and
password, and create the video bucket
