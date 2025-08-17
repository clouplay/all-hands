FROM ubuntu:22.04

# Sistem güncellemeleri ve temel araçlar
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nodejs \
    npm \
    git \
    curl \
    wget \
    vim \
    nano \
    tree \
    htop \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python paketleri
RUN pip3 install \
    requests \
    numpy \
    pandas \
    matplotlib \
    jupyter \
    flask \
    fastapi \
    uvicorn

# Node.js global paketleri
RUN npm install -g \
    typescript \
    ts-node \
    nodemon \
    create-react-app

# Çalışma dizini
WORKDIR /workspace

# Güvenlik için non-root user
RUN useradd -m -s /bin/bash sandbox
RUN chown -R sandbox:sandbox /workspace
USER sandbox

CMD ["/bin/bash"]