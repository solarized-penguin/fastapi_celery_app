FROM python:3.12

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY ./pyproject.toml ./poetry.lock* /app/

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry config virtualenvs.in-project true

RUN python -m venv venv

RUN poetry install



ENTRYPOINT [""]
