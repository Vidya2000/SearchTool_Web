FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV DB_HOST=localhost
ENV DB_PORT=3333
ENV DB_USER=root
ENV DB_PASSWORD=root
ENV DB_NAME=searchtool
EXPOSE 6061
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=production
CMD ["python", "app.py"]