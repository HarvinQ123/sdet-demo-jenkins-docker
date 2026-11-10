# Jenkins LTS + Python + Chromium, with the pipeline plugins preinstalled.
FROM jenkins/jenkins:lts-jdk21

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3 python3-venv python3-pip chromium chromium-driver fonts-liberation \
 && rm -rf /var/lib/apt/lists/*
USER jenkins

# Pipeline, Git checkout, JUnit test reports, and the stage-view grid on the job page.
RUN jenkins-plugin-cli --plugins workflow-aggregator git junit pipeline-stage-view

# Creates the "sdet-lab" job on first boot (see init.groovy.d/create-job.groovy).
COPY init.groovy.d/ /usr/share/jenkins/ref/init.groovy.d/

# Mounted project is owned by another uid; let git use it anyway.
RUN git config --global --add safe.directory '*'

# Skip the setup wizard (local lab only), and allow checkout from file:///project.
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false -Dhudson.plugins.git.GitSCM.ALLOW_LOCAL_CHECKOUT=true"
