# Start from the official PyTorch image without CUDA support for a lighter build
FROM python:3.11.5-slim

# Set the working directory in the container
WORKDIR /usr/src/AIapp
ARG PORT=5000
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    cmake \
    build-essential

# Install ONNX Runtime for CPU, Flask, InsightFace, OpenCV, and ensure torch is updated
RUN pip install --no-cache-dir onnxruntime==1.16.2 opencv-python
RUN pip install insightface==0.7.3
# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE $PORT

# Command to run the Flask app
CMD [ "python3", "main.py"]
