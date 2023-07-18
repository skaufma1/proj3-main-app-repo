FROM python:3.8
# Prior to building a new image - place here the AWS access key details
#ENV AWS_ACCESS_KEY_ID=
#ENV AWS_SECRET_ACCESS_KEY=
ENV AWS_REGION=us-east-1
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_APP=app.py
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
