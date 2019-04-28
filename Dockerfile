#Airflow container

FROM tensorflow/tensorflow:1.3.0-py3

ARG AIRFLOW_VERSION=1.10.2
ARG AIRFLOW_HOME=/root/home/airflow
ARG HOST_MACHINE_HOME=/home/automation
ARG DOCKER_HOME=/root

ENV AIRFLOW_GPL_UNIDECODE=yes
ENV AIRFLOW_HOME=${AIRFLOW_HOME}
WORKDIR ${AIRFLOW_HOME}


# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8


RUN apt-get update -yqq\
   && apt-get upgrade -yqq\
   && apt-get install python3-dev -y \
   && apt-get install build-essential -y\
   && apt-get install python3-pip -y \
   && apt-get install vim -y \
   && apt-get install host -y \
   && apt-get install ssh -y \
   && apt-get install git -y \
   && pip3 install --upgrade pip \
   && apt-get autoremove -yqq --purge \
   && apt-get clean \
   && mkdir /root/home/airflow -p \
   && apt-get install libpq-dev -y\
   && pip install apache-airflow[crypto,postgres,jdbc,password,ssh${AIRFLOW_DEPS:+,}${AIRFLOW_DEPS}]==${AIRFLOW_VERSION}


COPY requirements.txt /root/requirements.txt

RUN cd /root \
    && pip install --upgrade pip\
    && pip install -r requirements.txt

RUN apt-get install netcat -y

COPY script/entrypoint.sh /entrypoint.sh
COPY config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg
EXPOSE 8080

RUN mkdir ~/.ssh

WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT ["/entrypoint.sh"]
CMD ["webserver"] # set default arg for entrypoint
