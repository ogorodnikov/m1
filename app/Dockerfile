# FROM ubuntu:latest
FROM public.ecr.aws/lts/ubuntu:latest

RUN echo "Installing Python"

RUN apt-get update && \
    apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    git \
    && apt-get clean

RUN echo `python3 --version`

RUN python3 -m venv /m1_venv
ENV PATH="/m1_venv/bin:$PATH"

RUN pip install --upgrade pip 

RUN echo "Copying M1 files"

COPY ./core-service /m1-core-service
WORKDIR /m1-core-service

RUN echo "Installing M1 package"

RUN pip install .
RUN pip list

RUN echo "Starting Flask"

ENTRYPOINT ["python3"]
CMD ["run.py"]

# ENTRYPOINT ["bash"]
# CMD ["gunicorn.sh"]
