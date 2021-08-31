FROM python:3.7-slim

LABEL base_image="python:3.7-slim"
LABEL about.home="https://github.com/Clinical-Genomics/vogue"
LABEL about.documentation="https://vogue.readthedocs.io/"
LABEL about.license="MIT License (MIT)"

ENV GUNICORN_WORKERS=1
ENV GUNICORN_THREADS=1
ENV GUNICORN_BIND="0.0.0.0:8000"
ENV GUNICORN_TIMEOUT=400
ENV DB_URI="mongodb://localhost:27017/vogue-demo"
ENV DB_NAME="vogue-demo"

# Copy all project files
WORKDIR /home/vogue/vogue
COPY . /home/vogue/vogue

# Added pip install path
ENV PATH="/home/vogue/.local/bin:${PATH}"

# Install vogue
RUN cd /home/vogue/vogue && pip install --no-cache-dir -r requirements.txt
RUN cd /home/vogue/vogue && pip install --no-cache-dir -e .



CMD gunicorn \
    --workers=$GUNICORN_WORKERS \
    --bind=$GUNICORN_BIND  \
    --threads=$GUNICORN_THREADS \
    --timeout=$GUNICORN_TIMEOUT \
    --proxy-protocol \
    --forwarded-allow-ips="10.0.2.100,127.0.0.1" \
    --log-syslog \
    --access-logfile - \
    --log-level="debug" \
    vogue.server.auto:app
