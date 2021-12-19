FROM python:latest
WORKDIR /backend
RUN pip3 install asyncpg
RUN pip3 install dolon==0.1.2
COPY server.py server.py
CMD ["python", "server.py"]
