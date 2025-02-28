FROM python:3.10-slim


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=shareride.settings
ENV DATABASE_URL=postgres://postgres:Athulkjose123.@postgres.ctcsogy4gek9.eu-north-1.rds.amazonaws.com:5432/ShareRide
ENV SECRET_KEY=django-insecure-$(=ul33q32p^b%rmik6r)@ki5g(7_ofdw^ojg&)*4c#ww^!--o
ENV EMAIL_HOST_USER=athul.23pmc116@mariancollege.org
ENV EMAIL_HOST_PASSWORD = zklgvlvjrkjaprmv
ENV GROQ_API_KEY=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
ENV GOOGLE_MAPS_API_KEY=AIzaSyBnX3vMyrAvLILwOvs7c8P9soMWP7D3TEI


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