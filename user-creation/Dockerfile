FROM python:3.10-alpine
COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt
COPY . /opt/app

ENTRYPOINT [ "/usr/local/bin/python", "deploy.py" ]