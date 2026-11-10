#!/usr/bin/env bash
# Build and start the lab Jenkins in Docker (via Colima), with the job already created.
# Jenkins is bound to 127.0.0.1 only and has no login: it's a local lab, not a server.
set -euo pipefail
cd "$(dirname "$0")/.."
PROJECT_DIR="$(pwd)"
IMAGE=sdet-lab-jenkins
CONTAINER=sdet-jenkins

# 1. Docker engine: start Colima if Docker isn't answering.
if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Starting Colima ..."
  colima start
fi

# 2. Jenkins checks code out of Git, so the project must be a repo with a commit.
if [ ! -d .git ]; then
  echo "Initializing Git repo (branch main) ..."
  git init -q -b main
fi
if ! git rev-parse --verify -q HEAD >/dev/null; then
  git add -A
  git commit -q -m "Initial SDET lab commit"
  echo "Made the first commit."
fi

# 3. Build the image (Jenkins + Python + Chromium + plugins). Cached after the first run.
echo "Building image $IMAGE (first build takes a few minutes) ..."
docker build -t "$IMAGE" jenkins/

# 4. Replace any old container, keep the jenkins_home volume (build history).
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
docker run -d --name "$CONTAINER" \
  -p 127.0.0.1:8080:8080 \
  --shm-size=1g \
  -v sdet-jenkins-home:/var/jenkins_home \
  -v "$PROJECT_DIR":/project:ro \
  "$IMAGE" >/dev/null

# 5. Wait for Jenkins to answer.
printf "Waiting for Jenkins to start "
for _ in $(seq 1 90); do
  if curl -fs -o /dev/null http://127.0.0.1:8080/login 2>/dev/null \
     || curl -fs -o /dev/null http://127.0.0.1:8080/ 2>/dev/null; then
    echo
    echo "Jenkins is up:  http://127.0.0.1:8080/job/sdet-lab/"
    exit 0
  fi
  printf "."
  sleep 2
done
echo
echo "Jenkins did not answer after 3 minutes. Check:  docker logs $CONTAINER"
exit 1
