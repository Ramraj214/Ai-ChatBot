# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Update pip and install system dependencies
RUN pip install --upgrade pip && \
    apt-get update && \
    apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application’s code into the container
COPY . .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable
ENV STREAMLIT_SERVER_PORT=8501

# Define environment variable
ENV MONGODB_URI="mongodb://15.206.170.219:27017/test"
ENV GOOGLE_API_KEY="AIzaSyC_itBcDuD0jKIYLpcnD6y-pWSdud_tyTY"

# Run Streamlit when the container launches
CMD ["streamlit", "run", "app.py"]
