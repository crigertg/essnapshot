FROM docker.elastic.co/elasticsearch/elasticsearch:7.9.0
RUN mkdir -p /mnt/snapshot && chown elasticsearch:elasticsearch /mnt/snapshot