FROM python:3.9

ADD requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt
ADD main.py /main.py
ADD db.py /db.py
EXPOSE 5000
CMD ["python3", "main.py"]


HEALTHCHECK CMD curl --fail http://localhost:5000 || exit 1