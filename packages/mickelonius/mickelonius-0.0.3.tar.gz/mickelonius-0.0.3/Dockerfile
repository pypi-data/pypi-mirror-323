FROM ubuntu:20.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

## OS pkgs, deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-11-jdk \
    wget \
    git \
    curl \
    git \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python3-openssl && \
    rm -rf /var/lib/apt/lists/*

ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
RUN git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT
RUN echo 'export PYENV_ROOT="/root/.pyenv"' >> ~/.bashrc && \
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && \
    echo 'eval "$(pyenv init --path)"' >> ~/.bashrc && \
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Install a specific Python version and set it globally
RUN /bin/bash -c "source /root/.bashrc && \
    pyenv install 3.12.8 && \
    pyenv global 3.12.8 && \
    pyenv rehash"

# Verify installation
RUN /bin/bash -c "source /root/.bashrc && \
    python --version && pip --version"


## Spark
ENV SPARK_VERSION=3.5.4
ENV HADOOP_VERSION=3
RUN wget -nv https://downloads.apache.org/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz && \
    tar -xvf spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz -C /opt && \
    rm spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz && \
    ln -s /opt/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION /opt/spark
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV SPARK_HOME=/opt/spark
ENV PATH="$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH"


WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir .
RUN pip install -r requirements.txt -r requirements-test.txt
RUN pip install -U six setuptools wheel setuptools-scm twine

#CMD ["python"]
