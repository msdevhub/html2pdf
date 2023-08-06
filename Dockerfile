FROM python:3.9-slim-buster

WORKDIR /app

# 将软件源配置为阿里云镜像源
RUN echo "deb http://mirrors.aliyun.com/debian/ buster main" > /etc/apt/sources.list \
    && echo "deb-src http://mirrors.aliyun.com/debian/ buster main" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ buster-updates main" >> /etc/apt/sources.list \
    && echo "deb-src http://mirrors.aliyun.com/debian/ buster-updates main" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian-security/ buster/updates main" >> /etc/apt/sources.list \
    && echo "deb-src http://mirrors.aliyun.com/debian-security/ buster/updates main" >> /etc/apt/sources.list
    
COPY . .
RUN apt-get update && apt-get install -y \
    wkhtmltopdf libcairo2-dev gcc\
    xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY ./fonts/** /usr/share/fonts
RUN fc-cache -f -v

EXPOSE 8501

CMD ["streamlit", "run", "--server.enableCORS", "false", "main.py"]
