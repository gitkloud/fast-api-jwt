FROM python:3.12.8-alpine3.20

# Set the working directory
ENV APP_HOME /app

# Create the working directory
WORKDIR $APP_HOME

COPY main.py requirements.txt ./
COPY app/ app/

# Install the dependencies
RUN pip install -r requirements.txt

# Expose the port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
