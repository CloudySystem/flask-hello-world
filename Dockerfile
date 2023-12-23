FROM python:3.8-slim-buster

WORKDIR /app

RUN pip install Flask

COPY app.py .

ENV FLASK_APP=app.py

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
