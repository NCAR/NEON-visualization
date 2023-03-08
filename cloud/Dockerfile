FROM continuumio/anaconda3

WORKDIR /apps

COPY . .

ENV PORT=8080

RUN chown 1000:1000 /opt/conda/ && \
    chmod 777 entrypoint.sh

ARG USER=bokeh
RUN useradd -s /bin/bash -m ${USER}
USER ${USER}

RUN conda create --name neon -c conda-forge python=3.9 numpy scipy matplotlib pandas netcdf4 jupyter xarray tqdm bokeh jupyterlab fsspec ujson gcsfs dask zarr

RUN echo "conda activate neon" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

ENTRYPOINT ["./entrypoint.sh"]
