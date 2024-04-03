FROM python:latest

RUN mkdir -p /home/sensor/cluster_app && \ 
    useradd -d /home/sensor sensor

SHELL [ "/bin/bash" ]

USER sensor
WORKDIR /home/sensor

ADD ./cluster_app /home/sensor/cluster_app

# ENTRYPOINT [ "/home/sensor/cluster_app/run.sh" ]

ENTRYPOINT [ "tail", "-f", "/dev/null" ]

# docker build . -t sensor
# docker run --detach --name sensor0 --net="host" sensor
# docker exec -it sensor0 bash
