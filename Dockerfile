FROM python:3.10.0b3-slim-buster
LABEL author="Colin"
LABEL maintainer="Colin_XKL@outlook.com"
LABEL homepage="https://github.com/Colin-XKL/TTRSS-Dashboard"
COPY . .
RUN pip install -r requirements.txt
ENV FLASK_ENV production
ENTRYPOINT [ "python3","app.py" ]
EXPOSE 5000