FROM ubuntu:latest

WORKDIR /usr/local/src

VOLUME /usr/local/src
VOLUME /usr/local/lib/python3.6/dist-packages

ADD ./docker/entrypoint /usr/bin/entrypoint

RUN apt-get update
RUN apt-get -y install python3.6 python3-pip

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENTRYPOINT ["entrypoint"]
CMD ["scripts/devServer"]
