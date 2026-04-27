FROM python:3.11-slim

# Set working directory
WORKDIR /opt/buildon

# Install Project requirements
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .



EXPOSE 8001
CMD bash config/run.sh

