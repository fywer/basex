FROM python:3.8
WORKDIR /basex
COPY requeriments.txt
RUN pip install -r requeriments.txt
COPY /src
CMD ["python", "./main.py"] 
