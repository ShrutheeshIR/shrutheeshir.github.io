FROM klakegg/hugo:ext-ubuntu

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3-pip

RUN pip3 install academic==0.5.1 --break-system-packages

RUN apt-get install -y ssh-askpass sshpass rsync
# Copies your code file from your action repository to the filesystem path `/` of the container
# COPY entrypoint.sh /entrypoint.sh

# RUN ["chmod", "+x", "/entrypoint.sh"]

# # Code file to execute when the docker container starts up (`entrypoint.sh`)
# ENTRYPOINT ["/entrypoint.sh"]
ENTRYPOINT ["/bin/bash", "-l", "-c"]