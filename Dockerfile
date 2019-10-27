FROM python:3.7.1

ENV PYTHONUNBUFFERED 1
USER root
WORKDIR /app
ADD . /app
# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
RUN apt-get update
RUN apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev
RUN pip install --upgrade pip
RUN pip install -r /requirements/local.txt
RUN chmod -R g+rwx /app /requirements
USER 1001