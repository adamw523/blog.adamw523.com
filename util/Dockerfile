FROM ubuntu

RUN apt-get update && apt-get install -y less \
        curl vim less python-setuptools mysql-client

RUN easy_install pip
RUN pip install boto

COPY restore_wp_content_from_url.sh /
COPY restore_db_from_url.sh /
COPY backup_db_to_s3.sh /
COPY backup_wp_content_to_s3.sh /
RUN chmod +x /*.sh

CMD ["/bin/bash", "-c", "while true; do :; sleep 1; done"]
