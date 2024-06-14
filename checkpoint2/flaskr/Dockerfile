FROM python:3.12-alpine

# Set the working directory within the container
WORKDIR /DBMi-flask

# Copy the necessary files and directories into the container
COPY ./algo.py ./db.py ./app.py ./auth.py ./routes.py ./password.txt /DBMi-flask
COPY ./requirements.txt ./api_routes.py ./sessionkey.txt ./static/* /DBMi-flask

RUN apk update \
    && apk --no-cache --update add build-base 

RUN pip3 install --upgrade pip && pip install -r requirements.txt

# Expose port 5000 for the Flask application
EXPOSE 5014

CMD python -m flask --no-debug run --port=5014
