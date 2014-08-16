# Version 0.1

FROM	dockerfile/ubuntu

# Install python
RUN	\
	apt-get install -y -qq python python-dev python-pip

# Copy Source
RUN \
    mkdir /src; cd /src; git clone https://github.com/abh1nav/mapper.git

# Install dependencies
RUN \
    cd /src/mapper; pip install -r requirements.txt

EXPOSE 5000

WORKDIR /src/mapper

CMD ["python", "server.py"]
