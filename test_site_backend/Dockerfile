FROM python:3.8.2
MAINTAINER Aleksei Fomin

COPY back /app/back
COPY requirements.txt /app
COPY entrypoint.sh /app
COPY main.py /app
COPY pytest.ini /app
WORKDIR /app

RUN pip install -r ./requirements.txt
RUN chmod +x entrypoint.sh

EXPOSE 9090

CMD ["./entrypoint.sh"]
