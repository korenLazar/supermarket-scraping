FROM debian:latest as dev
WORKDIR /usr/src/app

# setting the enviroment 
RUN apt-get update -y && apt-get install cron -y && apt-get install libxml2-dev -y && apt-get install libxslt-dev -y && apt-get install gcc-10 -y && apt-get install g++-10 -y && apt-get install -y python3-pip && apt-get install -y dieharder
RUN apt-get -y install git
COPY . .
RUN pip install -r requirements.txt