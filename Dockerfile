FROM ubuntu:xenial
RUN apt-get update 
RUN apt-get install -y build-essential software-properties-common python-software-properties
RUN apt-get update 
RUN add-apt-repository ppa:webupd8team/java && apt-get update
RUN echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | debconf-set-selections
RUN echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 seen true" | debconf-set-selections
RUN apt-get update 
RUN apt-get install -y oracle-java8-installer maven \
    python-dev python-pip python-virtualenv \
    libsasl2-dev libldap2-dev libssl-dev \
    npm nodejs nodejs-legacy && \
    npm install avrodoc -g
ENV PYTHONUNBUFFERED 1
RUN mkdir /gel
RUN mkdir /gel/GelReportModels
WORKDIR /gel
ADD . /gel/GelReportModels
ADD m2_settings.xml /gel
RUN mkdir -p ~/.m2 && cp m2_settings.xml ~/.m2/settings.xml
RUN cd ./GelReportModels && \
    pip install --upgrade pip==9.0.3 && \
    pip install . && \
    pip install --upgrade pysam && \
    python build.py --skip-docs --skip-java
