FROM ubuntu:latest
RUN echo Updating existing packages, installing and upgrading python and pip.
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
RUN pip3 install --upgrade pip
RUN echo Copying the M1 Core Service into a service directory.
COPY ./core-service /m1-core-service
WORKDIR /m1-core-service
RUN echo Installing Python packages listed in requirements.txt
RUN pip3 install -r ./requirements.txt
RUN echo Starting python and starting the Flask service...
ENTRYPOINT ["python3"]
CMD ["core_service.py"]
