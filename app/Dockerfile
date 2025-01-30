FROM public.ecr.aws/docker/library/python:3.12-slim

RUN python3 -m venv /m1_venv && \
    pip install --upgrade pip

ENV PATH="/m1_venv/bin:$PATH"

RUN echo "Copy M1 Core files"

COPY ./core-service /m1-core-service
WORKDIR /m1-core-service

RUN echo "Install M1 package"

RUN pip install .
RUN pip list

RUN echo "Start Flask"

ENTRYPOINT ["python3"]
CMD ["run.py"]

# ENTRYPOINT ["bash"]
# CMD ["gunicorn.sh"]