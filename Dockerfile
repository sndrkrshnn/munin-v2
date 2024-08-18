FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

ENV OPENAI_API_KEY sk-proj-FomcOA0Ki3x5Sk2WERo0T3BlbkFJiShYtnFHtNh12QbODdyU
EXPOSE 8080
CMD ["python", "main.py"]