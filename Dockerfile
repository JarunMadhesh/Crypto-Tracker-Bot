FROM python:3.10.4
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD python main.py