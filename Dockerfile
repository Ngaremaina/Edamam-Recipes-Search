# ---- Stage 1: build Tailwind CSS ----
FROM node:26-alpine AS assets
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY tailwind.config.js ./
COPY recipes/templates ./recipes/templates
COPY recipes/static/recipes/src ./recipes/static/recipes/src
RUN npm run build

# ---- Stage 2: Python runtime ----
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=assets /app/recipes/static/recipes/dist ./recipes/static/recipes/dist

# Placeholder values so `collectstatic` can run at build time; the real
# secrets are supplied at container runtime via env vars / --env-file.
RUN SECRET_KEY=build-time-placeholder \
    EDAMAM_APP_ID=build-time-placeholder \
    EDAMAM_APP_KEY=build-time-placeholder \
    python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn recipe_search_engine.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
