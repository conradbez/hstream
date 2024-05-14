
FROM python:3.11-slim
WORKDIR /code

RUN pip install --upgrade pip
RUN pip install hstream
# COPY requirements.txt /code/
# RUN pip install -r requirements.txt # uncomment if you have a requirements.txt
COPY . /code/
CMD hstream run ./app
