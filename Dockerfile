FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 6061
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=production
CMD ["python", "app.py"]