#!/bin/bash
user_access='sudo' # '' or 'sudo'

# Step 0
$user_access docker builder prune -a -f
$user_access docker system prune -a -f

$user_access docker stop $($user_access docker ps -aq) # stop all running containers
$user_access docker rm $($user_access docker ps -aq) # remove all containers
$user_access docker rmi $($user_access docker images -aq) # remove all images
$user_access docker volume rm $($user_access docker volume ls -q) # remove all volumes
$user_access docker network rm $($user_access docker network ls -q) # remove all networks

source scripts/kill_yum_lock.sh

echo "****** end of step 0"



# Step 1
$user_access yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine \
                  docker-ce \
                  docker-ce-cli \
                  docker-compose-plugin \
                  podman \
                  runc -y

source scripts/kill_yum_lock.sh
echo "****** end of step 1"

# Step 2
$user_access yum install -y yum-utils

source scripts/kill_yum_lock.sh
echo "****** end of step 2"

# Step 3
$user_access yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

source scripts/kill_yum_lock.sh
echo "****** end of step 3"

# Step 4
$user_access yum install docker-ce-23.0.1 docker-ce-cli-23.0.1 containerd.io docker-buildx-plugin docker-compose-plugin -y
source scripts/kill_yum_lock.sh

echo "****** end of step 4"

# Step 4.1
$user_access service docker start
echo "****** end of step 4.1"

# Step 4.2
$user_access service docker stop
echo "****** end of step 4.2"

# Step 4.3
$user_access service docker start
echo "****** end of step 4.3"

# Step 5
$user_access docker login -u <your_user_name> -p <your_password>

echo "****** end of step 5"

# Step 6
$user_access service docker stop
echo "****** end of step 6"

# Step 7
$user_access rm -rf /var/lib/docker/*
echo "****** end of step 7"

# Step 8
$user_access rm -rf /var/lib/docker
echo "****** end of step 8"

# Step 9
$user_access rm -rf /var/lib/docker 2>&1 | awk '{print $4}' | tr -d ':‘’' | xargs sudo umount -lf
echo "****** end of step 9"

# Step 10
df -h /var/lib/docker
echo "****** end of step 10"

# Step 11
$user_access service docker start
echo "****** end of step 11"

# Step 12
$user_access service docker stop
echo "****** end of step 12"

# Step 13
$user_access service docker start
echo "****** end of step 13"

# Step 14
df -h /var/lib/docker
$user_access du -h /var/lib/docker/
echo "****** end of step 14"

# Step 15
source scripts/kill_yum_lock.sh