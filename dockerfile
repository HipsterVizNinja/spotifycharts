FROM python:3.9.1-slim
RUN pip install fastapi uvicorn spotifycharts
COPY ./application /application