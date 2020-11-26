# Docker for compiling AWS Lambda functions written in Python 3.7
FROM amazonlinux:2.0.20191016.0

RUN yum install -y python37 && \
    yum install -y python3-pip && \
    yum install -y zip && \
    yum clean all

RUN yum install -y unzip

RUN curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip" && \
    unzip awscli-bundle.zip && \
    ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws
    # yum install -yy less

RUN python3.7 -m pip install --upgrade pip && \
    python3.7 -m pip install virtualenv

# AWS user: docker-lambda-compiler
ENV AWS_ACCESS_KEY_ID="<YOUR ACCESS KEY ID>"
ENV AWS_SECRET_ACCESS_KEY="<YOUR SECRET ACCESS KEY>"
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./app /app
WORKDIR /app

RUN chmod +x deploy.sh
ENTRYPOINT [ "bash", "deploy.sh" ]