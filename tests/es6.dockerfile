FROM docker.elastic.co/elasticsearch/elasticsearch:7.8.1
RUN mkdir -p /mnt/snapshot && chown elasticsearch:elasticsearch /mnt/snapshot