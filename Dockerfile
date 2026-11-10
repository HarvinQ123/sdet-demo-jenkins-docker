# Test-runner image: the API + Playwright suites run the same way on any machine or CI host.
#   docker build -t sdet-lab-tests .
#   docker run --rm -v "$PWD/reports:/work/reports" sdet-lab-tests
# The base image is Microsoft's official Playwright image; its version matches requirements.txt,
# so Chromium and all its system libraries are already installed.
FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /work
ENV PYTHONDONTWRITEBYTECODE=1 PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependencies first, so this layer is cached until requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pytest.ini .
COPY app/ app/
COPY tests/ tests/

# Run as the image's non-root user; reports/ is where results land (mount it to keep them).
RUN mkdir -p reports && chown -R pwuser:pwuser /work
USER pwuser

# Selenium UI tests need Chrome + chromedriver and run in the Jenkins image instead.
ENTRYPOINT ["pytest", "-m", "api or playwright", "--junitxml=reports/docker.xml"]
