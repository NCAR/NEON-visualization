FROM continuumio/anaconda3:2022.10

WORKDIR /apps

COPY . .

ENV PORT=8080

RUN chown 1000:1000 /opt/conda/ && \
    chmod 777 entrypoint.sh

ARG USER=bokeh
RUN useradd -s /bin/bash -m ${USER}
USER ${USER}

RUN conda create --name neon -c conda-forge python=3.10 numpy=1.24 scipy=1.10 matplotlib=3.7 pandas=1.5 netcdf4=1.6 jupyter=1.0 xarray=2023 tqdm=4.65 bokeh=2.4 jupyterlab=3.5 fsspec=2023 ujson=5.7 gcsfs=2023 dask=2023 zarr=2.14 pillow=8.4

RUN echo "conda activate neon" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

ENTRYPOINT ["./entrypoint.sh"]
