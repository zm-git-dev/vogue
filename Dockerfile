FROM python:3.7-slim

LABEL base_image="python:3.7-slim"
LABEL about.home="https://github.com/Clinical-Genomics/vogue"
LABEL about.documentation="https://vogue.readthedocs.io/"
LABEL about.license="MIT License (MIT)"

# Update apt-get and then cleanup
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Copy all project files
WORKDIR /home/vogue/vogue
COPY . /home/vogue/vogue

# Create a user named vogue and run as vogue
RUN useradd --create-home --shell /bin/bash vogue
RUN chown vogue:vogue -R /home/vogue
USER vogue

# Added pip install path
ENV PATH="/home/vogue/.local/bin:${PATH}"

# Install vogue
RUN cd /home/vogue/vogue && pip install --no-cache-dir -r requirements.txt
RUN cd /home/vogue/vogue && pip install --no-cache-dir -e .

EXPOSE 5000