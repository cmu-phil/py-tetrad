FROM eclipse-temurin:11-jdk-jammy

RUN apt update
RUN apt upgrade -y
RUN apt install -y git
RUN apt install -y build-essential 

# the following adds python3.10
RUN apt install -y software-properties-common

RUN apt install -y python3-dev python3-venv
RUN apt install -y python3-pip
RUN apt install -y libsasl2-dev libldap2-dev libssl-dev

# install jpype and other python packages
COPY requirements.txt .
RUN pip install -r requirements.txt


