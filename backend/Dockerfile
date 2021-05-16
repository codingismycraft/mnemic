FROM python:latest
WORKDIR /backend
RUN pip3 install asyncpg
COPY constants.py constants.py
COPY dbconn.py dbconn.py
COPY server.py server.py
COPY utils.py utils.py
ENV PYTHONPATH "${PYTHONPATH}:."
CMD ["python", "server.py"]
