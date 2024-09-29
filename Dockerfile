FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=shareride.settings
ENV DATABASE_URL=postgres://postgres:Cricket123.@database-1.ctcsogy4gek9.eu-north-1.rds.amazonaws.com:5432/ShareRide
ENV SECRET_KEY=django-insecure-$(=ul33q32p^b%rmik6r)@ki5g(7_ofdw^ojg&)*4c#ww^!--o
ENV EMAIL_HOST_USER=athul.23pmc116@mariancollege.org
ENV EMAIL_HOST_PASSWORD = 23pmc116123.@
ENV GEMINI_API_KEY=AIzaSyA2kUpaFZjcR0wmYNVhh8GH3kSfso7pv80

# Set work directory
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /usr/src/app/

# Expose the port your app runs on
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]