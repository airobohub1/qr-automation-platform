
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY start-api.sh /app/start-api.sh
COPY start-streamlit.sh /app/start-streamlit.sh

RUN chmod +x /app/start-api.sh
RUN chmod +x /app/start-streamlit.sh


EXPOSE 8000
EXPOSE 8501


ARG START_SCRIPT=start-api.sh
# CMD ["/app/${START_SCRIPT}"]

CMD ["/app/start-api.sh"]

# CMD ["./start.sh"]
# CMD ["./start-api.sh"]





# FROM python:3.12-slim

# WORKDIR /app

# ENV PYTHONPATH=/app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 8501

# CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
