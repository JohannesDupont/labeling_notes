FROM python:3.9-slim

RUN apt-get update \
    && apt-get install -y \
        python3-tk \
        tcl8.6-dev \
        tk8.6-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#WORKDIR /app

COPY code/app.py ./app.py

COPY finished_labeling ./finished_labeling

COPY notes_to_label ./notes_to_label

RUN pip install --trusted-host pypi.python.org pandas

CMD ["python3", "app.py"]



