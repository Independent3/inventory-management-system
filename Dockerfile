FROM python:3.11-slim

#create isolated workspace
WORKDIR /app

COPY requirements.txt .
#install dependencies without cache
RUN pip install --no-cache-dir -r requirements.txt

#copy all project files into container
COPY . .
#documentation - listens to port 5000
EXPOSE 5000
#Start flask app when container runs
CMD ["python", "app.py"]