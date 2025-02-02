FROM tiangolo/uvicorn-gunicorn:python3.11

LABEL maintainer="Nuo Wen Lei <nuowen0612@gmail.com>"

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]