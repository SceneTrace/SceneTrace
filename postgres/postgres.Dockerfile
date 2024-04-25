FROM postgres:latest

RUN echo "en_US.UTF-8 UTF-8"> /etc/locale.gen
RUN locale-gen

RUN sed -i -e"s/^#maintenance_work_mem = 64MB.*$/maintenance_work_mem = 512MB/" /var/lib/postgresql/data/postgresql.conf

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    postgresql-server-dev-all \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /tmp
RUN git clone https://github.com/pgvector/pgvector.git

WORKDIR /tmp/pgvector
RUN make
RUN make install