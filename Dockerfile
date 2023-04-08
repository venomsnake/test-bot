FROM python:3.10.7

WORKDIR /root/Nibb

COPY . .

RUN pip3 install -r requirements.txt

CMD ["python3","-m","Nibb"]