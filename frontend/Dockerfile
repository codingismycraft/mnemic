FROM jupyter/tensorflow-notebook
RUN pip3 install asyncpg
RUN pip3 install dolon==0.0.44
COPY . .
CMD ["python3", "server.py"]
