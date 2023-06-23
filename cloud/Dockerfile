FROM continuumio/anaconda3:2022.10

WORKDIR /apps

COPY . .

ENV PORT=8080

RUN chown 1000:1000 /opt/conda/ && \
    chmod 777 entrypoint.sh

ARG USER=bokeh
RUN useradd -s /bin/bash -m ${USER}
USER ${USER}

RUN conda env create -f environment.yml

RUN echo "conda activate neon" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

ENTRYPOINT ["./entrypoint.sh"]
