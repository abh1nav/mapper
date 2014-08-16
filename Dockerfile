# Version 0.2

FROM	dockerfile/ubuntu

# Install python
RUN	\
	apt-get install -y -qq python python-dev python-pip

# Copy Source
ADD .   /src

RUN \
    cd /src; git remote rm origin; git remote add origin https://github.com/abh1nav/mapper.git;

# Install dependencies
RUN \
    cd /src; pip install -r requirements.txt

EXPOSE 5000

WORKDIR /src

CMD ["/src/run.sh"]
