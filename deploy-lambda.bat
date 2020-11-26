docker rm lambdalayer-p37 && \
docker build -f Dockerfile -t lambdalayer-p37:latest . && \
docker run -it --name lambdalayer-p37 lambdalayer-p37:latest && \
docker rm lambdalayer-p37