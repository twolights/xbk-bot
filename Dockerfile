FROM python:2.7-alpine
MAINTAINER Evan Chen <twolights@gmail.com>

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py reset.py stickers.py ./

CMD ["python", "./bot.py"]
