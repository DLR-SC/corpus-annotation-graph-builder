FROM python:3.9

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir pytest pytest-sugar

RUN pip install --no-cache-dir .

CMD [ "pytest --verbose" ]
