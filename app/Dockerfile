# FROM ubuntu:latest
FROM public.ecr.aws/lts/ubuntu:latest

RUN echo "Updating existing packages, installing and upgrading python and pip"

RUN apt-get update && \
    apt-get install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    libhdf5-dev \
    && apt-get clean

RUN echo `python3 --version`

RUN python3 -m venv /m1_venv
ENV PATH="/m1_venv/bin:$PATH"

RUN pip install --upgrade pip 
RUN pip install setuptools wheel

RUN echo "Copying the M1 Core Service into service directory"

COPY ./core-service /m1-core-service
WORKDIR /m1-core-service

RUN echo "Installing Python packages listed in requirements.txt"

RUN pip install -r ./requirements.txt

RUN echo "Starting the Flask service"

ENTRYPOINT ["python3"]
CMD ["run.py"]

# ENTRYPOINT ["bash"]
# CMD ["gunicorn.sh"]
