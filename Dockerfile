FROM python:3.10.7-buster

RUN apt-get update && apt-get install -y git
ADD requirements.txt /requirements.txt
RUN pip install --no-deps git+https://github.com/jeslago/epftoolbox@master#egg=epftoolbox
RUN pip install -r /requirements.txt
RUN mkdir /app
WORKDIR /app
# Stop us importing tensorflow as not used
RUN echo "" > /usr/local/lib/python3.10/site-packages/epftoolbox/models/__init__.py
COPY ep_predict /app/ep_predict
RUN mkdir website
RUN python -m ep_predict
