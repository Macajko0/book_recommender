FROM python:3.10

ENV PYTHONUNBUFFERED 1

RUN apt-get -y update

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install uvicorn

CMD ["uvicorn", "main:app", "--reload"]