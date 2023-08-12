FROM python:3.9-slim-buster

WORKDIR /app

COPY . .
RUN apt-get update && apt-get install -y \
    wkhtmltopdf libcairo2-dev gcc\
    xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5
RUN pip install -r requirements.txt
COPY ./fonts/** /usr/share/fonts
RUN fc-cache -f -v

EXPOSE 8501

CMD ["streamlit", "run", "--server.enableCORS", "false", "main.py"]
