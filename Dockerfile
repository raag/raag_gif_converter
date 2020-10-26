FROM alpine:latest
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN apk update
RUN apk add python3 
RUN apk add ffmpeg 
RUN apk add py-pip
COPY app.py ./
COPY requirements.txt ./
RUN mkdir uploads

RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python3", "./app.py"]
