FROM python:3.10.4
RUN pip install -r requirements.txt
CMD python main.py
