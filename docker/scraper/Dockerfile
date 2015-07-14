# To build use:
# docker build -t orian/cppenv:v1 .
FROM ubuntu:15.04
MAINTAINER Pawel Szczur <public at pawelsz.eu>

LABEL description="container for running Olsztyn BIP scraper."

RUN echo 'deb http://ftp.icm.edu.pl/pub/Linux/ubuntu/ vivid restricted universe main' > /etc/apt/sources.list && echo 'deb-src http://ftp.icm.edu.pl/pub/Linux/ubuntu/ vivid restricted universe main' >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y \
  python \
  python-pip \
  python-libxml2 \
  libxml2-dev \
  python-libxslt1 \
  libxslt1-dev \
  python-dev \
  libffi-dev \
  libssl-dev \
  zlib1g-dev && \
  pip install Twisted Scrapy

  #libxml2 and libxslt

ENV LD_LIBRARY_PATH=/libs
ENV CPLUS_INCLUDE_PATH=/libs/include

RUN mkdir /src
RUN mkdir /data
WORKDIR /src

ENTRYPOINT ["scrapy"]