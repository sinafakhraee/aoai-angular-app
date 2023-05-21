# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /backend
WORKDIR /backend

# Add the current directory contents into the container at /myflaskapp
ADD . /backend

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.text

# Make port 80 available to the world outside this container
EXPOSE 5000

# Define environment variable
# ENV NAME World

# Run run.py when the container launches
CMD ["python", "app.py"]
