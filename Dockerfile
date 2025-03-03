FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    pandoc \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-plain-generic \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "your_script_name.py", "--server.port=8080", "--server.address=0.0.0.0"]
