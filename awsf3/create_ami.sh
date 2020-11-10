#!/bin/bash

# basic updates and installation
apt update
apt install -y awscli
apt install -y apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common  # docker

# install docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
apt-key fingerprint 0EBFCD88
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
apt update # update again with an updated repository
apt install -y docker-ce  # installing docker-ce
usermod -aG docker ubuntu  # making it available for non-root user ubuntu

