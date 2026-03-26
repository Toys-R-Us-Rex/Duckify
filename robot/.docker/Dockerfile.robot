FROM python:3.11-slim
# ubuntu:22.04

# The installer requires curl (and certificates) to download the release archive and a c++ compiler for pybullet
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    python3-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

RUN mkdir -p /app/robot
RUN mkdir -p /app/assets
RUN mkdir -p /app/3dmodel

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app

COPY robot_requirements.txt .

COPY ./robot/ ./robot/
COPY ./assets/ ./assets
COPY ./3dmodel/ ./3dmodel


# run `uv export --package robot --no-dev --no-hashes -o robot_requirements.txt` to get requirements
RUN uv pip install --no-cache --system -r robot_requirements.txt

# Set the working directory to where your main script is
WORKDIR /app/robot
CMD ["/bin/bash"]
# CMD ["python", "robot_main.py"]