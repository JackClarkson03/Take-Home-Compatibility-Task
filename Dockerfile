# Use the official Python 3.10 image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Whisper's system-level dependency (ffmpeg)
# If using conda locally, Docker still needs this system install
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy all project code into the container
# (This copies src/, data/, etc.)
COPY . .

# Tell the container which port to open (FastAPI default is 8000)
EXPOSE 8000

# The command to run the app when the container starts
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]