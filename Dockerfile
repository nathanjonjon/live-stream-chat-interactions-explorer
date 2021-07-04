FROM python:3.8
WORKDIR /code
COPY . .
RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc \
                                        libsndfile1 
RUN apt-get install ffmpeg -y
RUN pip install -r requirements.txt
RUN python3 -m spacy download en_core_web_sm

