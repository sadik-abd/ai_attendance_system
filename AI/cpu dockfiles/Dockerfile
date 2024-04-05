# Use an official PyTorch image with CUDA support as the parent image
FROM pytorch/pytorch:1.8.1-cuda11.1-cudnn8-runtime

# Set the working directory in the container
WORKDIR /usr/src/app

# Install ONNX Runtime for GPU, Flask, InsightFace, OpenCV, and ensure torch is updated
RUN pip install --no-cache-dir onnxruntime-gpu flask insightface opencv-python torch

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Command to run the Flask app
CMD [ "flask", "run", "--host=0.0.0.0" ]