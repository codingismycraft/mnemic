FROM python:latest
WORKDIR /backend
RUN pip3 install asyncpg
RUN pip3 install dolon==0.0.16
COPY server.py server.py
ENV POSTGRES_PASSWORD "postgres123"
ENV POSTGRES_USER "postgres"
ENV POSTGRES_DB "mnemic"
CMD ["python", "server.py"]
