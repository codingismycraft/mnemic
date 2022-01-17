FROM jupyter/tensorflow-notebook
RUN pip3 install asyncpg
RUN pip3 install dolon==0.2.0
COPY . .
CMD ["python3", "server.py"]
