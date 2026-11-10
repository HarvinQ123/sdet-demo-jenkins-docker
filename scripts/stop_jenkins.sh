#!/usr/bin/env bash
# Stop the lab Jenkins.
#   bash scripts/stop_jenkins.sh           stop and remove the container (keeps build history)
#   bash scripts/stop_jenkins.sh --purge   also delete build history (the jenkins_home volume)
#   Colima keeps running; stop it yourself with:  colima stop
set -euo pipefail
docker rm -f sdet-jenkins >/dev/null 2>&1 && echo "Jenkins container removed." || echo "No Jenkins container running."
if [ "${1:-}" = "--purge" ]; then
  docker volume rm sdet-jenkins-home >/dev/null 2>&1 && echo "Build history deleted." || true
fi
