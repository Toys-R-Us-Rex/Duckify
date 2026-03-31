FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl \
    libglib2.0-0 \
    libx11-6 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libgl1-mesa-glx \
    libegl1 \
    libfontconfig1 \
    libfreetype6 \
    libdbus-1-3 \
    # OpenGL and GLU
    libgl1-mesa-dev \
    libglu1-mesa \
    freeglut3-dev \
    # Docker CLI
    ca-certificates \
    gnupg \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && chmod a+r /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update && apt-get install -y docker-ce-cli

# Download UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY --parents pyproject.toml uv.lock ./*/pyproject.toml /app/

WORKDIR /app

RUN uv sync --frozen --no-install-local

COPY . /app

RUN uv sync --frozen

RUN uv run build-ui --frozen

CMD [ "uv", "run", "ui/main.py" ]