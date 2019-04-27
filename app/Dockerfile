FROM ubuntu:18.04
MAINTAINER MMV 'Marashan.M.V@sberbank.ru'
RUN apt-get update -y \
    && apt-get install -y apt-utils tzdata locales
RUN apt-get install -y python3-pip python3-dev build-essential \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && pip3 install --upgrade pip

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
     && echo $TZ > /etc/timezone
RUN set -xe &&\
    dpkg-reconfigure --frontend=noninteractive tzdata && \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    echo 'LANG="ru_RU.UTF-8"'>/etc/default/locale && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=ru_RU.UTF-8
ENV PYTHONIOENCODING=utf-8
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

RUN apt-get -y install portaudio19-dev

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt
