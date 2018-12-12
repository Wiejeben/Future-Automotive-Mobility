FROM python:3

RUN mkdir /code
WORKDIR /code

RUN pip install --upgrade pip

COPY Main /code

RUN pip install -r requirements.txt