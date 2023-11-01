FROM python:3.11-alpine
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
# requirements should not be reinstalled on every rebuild
COPY ./main.py ./.env .
CMD ["python", "main.py"]
