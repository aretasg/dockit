FROM continuumio/miniconda3

COPY environment.yml .
RUN conda env create -f environment.yml

COPY app /app/app
WORKDIR /app/app

CMD ["conda", "run", "-n", "dockit", "python", "dockit.py"]
