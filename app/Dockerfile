# FROM ubuntu:latest
FROM public.ecr.aws/lts/ubuntu:latest
RUN echo Updating existing packages, installing and upgrading python and pip
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
RUN apt-get install -y python3-venv
RUN python3 -m venv ~/m1_venv
RUN source ~/m1_venv/bin/activate
RUN pip3 install --upgrade pip
RUN echo Copying the M1 Core Service into service directory
COPY ./core-service /m1-core-service
WORKDIR /m1-core-service
RUN echo Installing Python packages listed in requirements.txt
RUN pip3 install -r ./requirements.txt
RUN echo Starting the Flask service
ENTRYPOINT ["python3"]
CMD ["run.py"]
# ENTRYPOINT ["bash"]
# CMD ["gunicorn.sh"]
