FROM python:3.8-slim-buster

RUN apt update -y && apt install awscli -y

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade accelerate

EXPOSE 7860

ENV GRADIO_SERVER_NAME="0.0.0.0"

CMD ["python", "app.py"]