# Capacity estimation CLI in a container: docker run --rm system-design-capacity url-shortener
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml ./
COPY tools ./tools
RUN pip install --no-cache-dir . && useradd --system --uid 10001 app
USER app
ENTRYPOINT ["capacity"]
CMD ["--list"]
