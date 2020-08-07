FROM docker.elastic.co/elasticsearch/elasticsearch:6.8.9
RUN mkdir -p /mnt/snapshot && chown elasticsearch:elasticsearch /mnt/snapshot