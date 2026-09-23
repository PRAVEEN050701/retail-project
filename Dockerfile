FROM python:3.12-slim

ENV APP_VERSION=4.2.0
ENV APP_ENV=UAT
ENV PAYMENT_STATUS=DEFECTIVE

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY app/app.py .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8081

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8081/health')" || exit 1

CMD ["python", "app.py"]