FROM python:3.9-slim-buster

WORKDIR /app

COPY . .
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 8501

CMD ["streamlit", "run", "--server.enableCORS", "false", "main.py"]
