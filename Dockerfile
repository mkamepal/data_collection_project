# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install --upgrade -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

#CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
CMD ["python3", "data_collection.py"]