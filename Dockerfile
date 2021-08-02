FROM python:3.9.1-buster

RUN mkdir /code
WORKDIR /code


RUN apt-get update && apt-get install -y --no-install-recommends xsltproc nmap git \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/vulnersCom/nmap-vulners /usr/share/nmap/scripts/nmap-vulners
RUN git clone https://github.com/scipag/vulscan /usr/share/nmap/scripts/vulscan

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir .