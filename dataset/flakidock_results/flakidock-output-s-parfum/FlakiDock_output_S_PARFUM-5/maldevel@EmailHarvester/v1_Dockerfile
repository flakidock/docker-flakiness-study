FROM alpine:edge


RUN apk --update add --no-cache python3 py3-requests py3-pip openssl ca-certificates
RUN apk --update --no-cache add --virtual build-dependencies python3-dev build-base wget git \
  && git clone https://github.com/maldevel/EmailHarvester.git
WORKDIR EmailHarvester

#COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python3", "EmailHarvester.py"]
CMD ["-h"]