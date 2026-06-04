FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mock_mcp_server.py .

ENV TRANSPORT=stdio

EXPOSE 8000

ENTRYPOINT ["python", "mock_mcp_server.py"]
