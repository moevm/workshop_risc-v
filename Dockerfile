FROM trampgeek/jobeinabox@sha256:1dfe026e8dd5cee4ea93bc7366207ae3e9910888d5dc343c85fb1508e8aebd8f

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && \
    apt install -y wget \
                   libglib2.0-dev \
                   libmpc-dev \
                   gcc \
                   nano \
                   vim && \
    wget -nv -O riscv-toolchain.tar.gz https://github.com/riscv-collab/riscv-gnu-toolchain/releases/download/2023.10.18/riscv64-glibc-ubuntu-22.04-gcc-nightly-2023.10.18-nightly.tar.gz && \
    tar -xf riscv-toolchain.tar.gz -C /opt/ && \
    rm riscv-toolchain.tar.gz

ENV PATH=/opt/riscv/bin:$PATH


WORKDIR /app
COPY requirements.txt requirements.txt
# Install requirements to cache them in docker layer
RUN pip3 install -r requirements.txt
COPY pyproject.toml README.md LICENSE ./
COPY main.py .
ENTRYPOINT ["python3", "main.py"]

ENV JAIL_PATH /tmp/jail
RUN mkdir ${JAIL_PATH} &&\
    cp -v --parents $(ldd $(which qemu-riscv64) | egrep -o '/lib.*\.[0-9]') ${JAIL_PATH} &&\
    cp $(which qemu-riscv64) ${JAIL_PATH}

COPY ./src ./src
RUN pip3 install . && rm -r src requirements.txt pyproject.toml
