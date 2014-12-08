FROM ubuntu

RUN apt-get update && apt-get install -y less \
        curl vim less python-setuptools mysql-client

RUN easy_install pip
RUN pip install boto

COPY restore_wp_content_from_url.sh /
COPY restore_db_from_url.sh /
