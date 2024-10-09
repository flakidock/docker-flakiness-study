## Detailed Examples of Error Categories

Below we provide examples of some of the most prevalent error categories, as well as FlakiDock's reponse. For simplicity, some parts are replaced with (...) to remove complexity Please download and see [flake4dock dataset](flake4dock) for further details.


### Dependency-Related Errors

#### Example (Retrieval/import Issues)

**Flaky Dockerfile**:

```Dockerfile
FROM python:2.7.15-slim

WORKDIR /usr/src/app

COPY . .

RUN set -ex  \
# error line:
&& apt update \
&& apt install -y build-essential python-dev\
&& pip install --no-cache-dir -r requirements.txt \
&& ...

EXPOSE 80

CMD ...
```

**Build Error**

```log
Reading package lists...
E: The repository 'http://deb.debian.org/debian stretch Release' does not have a Release file.
E: The repository 'http://deb.debian.org/debian stretch-updates Release' does not have a Release file.
E: The repository 'http://security.debian.org/debian-security stretch/updates Release' does not have a Release file.
```

**Cause of Error**
The debian repository in the base image is deprecated, resulted in retrieval failures in "apt update".

**FlakiDock's Response (Fixed)**

```Dockerfile
FROM node:lts-stretch

RUN echo "deb <mirror address> stretch main" > /etc/apt/sources.list \
  && echo "deb <mirror address> stretch-updates main" >> /etc/apt/sources.list \
  && echo "deb <mirror address> stretch/updates main" >> /etc/apt/sources.list

RUN set -ex \
  && apt-get update \
  && apt install -y build-essential python-dev\
  && pip install --no-cache-dir -r requirements.txt \
  && ...

EXPOSE 80

CMD ...
```

### Server Connectivity Errors

#### Example 1 (Internal Web Server Issues)

**Flaky Dockerfile**:

```Dockerfile
FROM daocloud.io/library/ubuntu:14.04

RUN ...

# error line:
RUN wget https://npm.taobao.org/mirrors/node/v8.9.1/node-v8.9.1-linux-x64.tar.gz && \
    tar -C /usr/local --strip-components 1 -xzf node-v8.9.1-linux-x64.tar.gz && \
    rm node-v8.9.1-linux-x64.tar.gz

WORKDIR /app

ADD package.json /app/package.json
RUN npm install --production -d --registry=https://registry.npm.taobao.org

COPY . /app

CMD ["node", "/app/server.js"]

```

**Build Error**

```log
ERROR: no certificate subject alternative name matches
	requested host name 'npm.taobao.org'.
```

**Cause of Error**
Internal issues within the repositories for nodejs.

**FlakiDock's Response (Fixed)**

```Dockerfile
FROM daocloud.io/library/ubuntu:14.04

RUN ...

RUN wget https://nodejs.org/dist/v8.9.1/node-v8.9.1-linux-x64.tar.gz && \
    tar -C /usr/local --strip-components 1 -xzf node-v8.9.1-linux-x64.tar.gz && \
    rm node-v8.9.1-linux-x64.tar.gz

WORKDIR /app

ADD package.json /app/package.json
RUN npm install --production -d --registry=https://registry.npmmirror.com

COPY . /app

CMD ["node", "/app/server.js"]
```

#### Example 2 (DNS Configuration Issues)

**Flaky Dockerfile**:

```Dockerfile
FROM phusion/baseimage:0.9.18

# error line:
RUN curl https://ossec.wazuh.com/repos/apt/conf/ossec-key.gpg.key -o ossec-key.gpg.key &&\
  apt-key add ossec-key.gpg.key && rm -v ossec-key.gpg.key &&\
  echo "deb http://ossec.wazuh.com/repos/apt/ubuntu trusty main" >> /etc/apt/sources.list &&\
  apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yf install expect ossec-hids \
  ossec-hids=2.8.3-4trusty

RUN ...
ENTRYPOINT ...
```

**Build Error**

```log
curl: (6) Could not resolve host: ossec.wazuh.com
```

**Cause of Error**
Host resolution failing. It can cause due to server temporary issues or DNS configuration problems.

**FlakiDock's Response (Not Fixed)**

```Dockerfile
FROM phusion/baseimage:0.9.18

RUN apt-get update && apt-get install -y curl gnupg && \
    curl https://packages.wazuh.com/key/GPG-KEY-WAZUH -o ossec-key.gpg.key && \
    apt-key add ossec-key.gpg.key && rm -v ossec-key.gpg.key && \
    echo "deb https://packages.wazuh.com/4.x/apt/ stable main" >> /etc/apt/sources.list && \
    apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yf install expect wazuh-agent=4.3.0-1

RUN ...
ENTRYPOINT ...
```

### Security and Authentication Errors
#### Example
**Flaky Dockerfile**:
```Dockerfile
FROM ubuntu:16.04

WORKDIR /app
ADD . /app

RUN ...

RUN curl -sL https://deb.nodesource.com/setup_9.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g nodemon eslint babel-eslint eslint-plugin-react yarn

RUN npm install

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4

# error line:
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/4.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.0.list

RUN ...
EXPOSE ...
```

**Build Error**
```log
E: The repository 'https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/4.0 Release' is not signed.
```

**Cause of Error**
The old repository with an outdated signature resulted in a build failure.


**FlakiDock's Response** 
```Dockerfile
FROM ubuntu:16.04 

WORKDIR /app
ADD . /app

RUN ...

RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g nodemon eslint babel-eslint eslint-plugin-react yarn

RUN npm install

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 9DA31620334BD75D9DCB49F368818C72E52529D4
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/4.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.0.list

RUN ...
EXPOSE ...
```

### Environment Errors
An example of this category alongside its repair is mentioned in Motivation section (Listing 2.1) as well as inside a figure (Figure 2) in the manuscript.
