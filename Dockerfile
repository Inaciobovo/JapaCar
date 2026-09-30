# JAPACAR - imagem de producao (Flask / Gunicorn, Python 3.12)
# O proprio projeto ja era multiplataforma; Python roda igual em ARM (Oracle Ampere A1)
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --system --uid 1001 --create-home appuser

WORKDIR /opt/app
COPY requirements.txt /opt/app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app /opt/app/app
COPY run.py gunicorn.conf.py /opt/app/

RUN mkdir -p /app/data/uploads && chown -R appuser:appuser /app

USER appuser
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=5 \
    CMD curl -fsS http://localhost:8080/login >/dev/null || exit 1

ENTRYPOINT ["gunicorn", "--config", "/opt/app/gunicorn.conf.py", "app:create_app()"]