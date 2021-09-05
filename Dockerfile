FROM python:2.7

LABEL maintainer="Charity Chepkirui"


COPY /techtrends /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 3111

# command to run on container start

CMD [ "python", "app.py"]