FROM python:3.11.11

ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt update && apt install -y wget && apt clean cache

COPY flaskapp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY flaskapp/ /code

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "some_app:app"]
