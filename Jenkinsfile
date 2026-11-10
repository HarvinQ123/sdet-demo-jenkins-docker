// Declarative pipeline: set up Python, run API tests, run headless UI tests,
// then publish JUnit results and archive reports (including failure screenshots).
// Every step is a plain bash command, so it runs the same way on your laptop.
pipeline {
    agent any

    environment {
        PYTHONDONTWRITEBYTECODE = '1'
    }

    stages {
        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install -q -r requirements.txt
                    mkdir -p reports
                    .venv/bin/python --version
                '''
            }
        }
        stage('API tests') {
            steps {
                sh '.venv/bin/pytest -m api --junitxml=reports/api.xml'
            }
        }
        stage('UI tests (headless Selenium)') {
            steps {
                sh '.venv/bin/pytest -m ui --junitxml=reports/ui.xml'
            }
        }
        stage('UI tests (Playwright)') {
            steps {
                // Downloads Playwright's own Chromium once (cached in the Jenkins home afterwards).
                // The image's apt chromium package already pulled in the system libraries it needs.
                sh '''
                    .venv/bin/playwright install chromium
                    .venv/bin/pytest -m playwright --junitxml=reports/playwright.xml
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/*.xml'
            archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/**'
        }
        success {
            echo "NOTIFY: ${env.JOB_NAME} #${env.BUILD_NUMBER} passed"
        }
        failure {
            // In a real team this would be a mail/Slack step; echo keeps the lab self-contained.
            echo "NOTIFY: ${env.JOB_NAME} #${env.BUILD_NUMBER} FAILED - see ${env.BUILD_URL}testReport/"
        }
    }
}
