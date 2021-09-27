FROM python:3-alpine

WORKDIR .

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "import secrets; print('SECRET_KEY = ' '\'' + secrets.token_urlsafe(32) + '\'')" > config.py
RUN python init_app.py

CMD ["python","app.py"]
