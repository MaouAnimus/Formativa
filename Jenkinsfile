pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'python3 -m venv .venv'
                sh '.venv/bin/python -m pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                sh '.venv/bin/python -m pytest -q'
            }
        }

        stage('Analyze') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                            "${scannerHome}/bin/sonar-scanner" \
                              -Dsonar.projectKey=formativa \
                              -Dsonar.sources=app.py \
                              -Dsonar.tests=tests
                        """
                    }
                }
            }
        }

        stage('Security Test') {
            steps {
                dependencyCheck(
                    odcInstallation: 'Dependency-Check',
                    additionalArguments: '--scan . --format XML --out dependency-check-report.xml'
                )
                dependencyCheckPublisher(pattern: 'dependency-check-report.xml')

                script {
                    try {
                        sh '''
                            docker network create formativa-net
                            docker build -t formativa-app .
                            docker run -d --rm --name formativa-app \
                              --network formativa-net formativa-app
                            docker run --rm --network formativa-net \
                              -v "$WORKSPACE:/zap/wrk:rw" \
                              ghcr.io/zaproxy/zaproxy:stable \
                              zap-baseline.py \
                              -t http://formativa-app:5000 \
                              -r zap-report.html -I
                        '''
                    } finally {
                        sh '''
                            docker rm -f formativa-app >/dev/null 2>&1 || true
                            docker network rm formativa-net >/dev/null 2>&1 || true
                        '''
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker build -t formativa-app .
                    docker rm -f formativa-app >/dev/null 2>&1 || true
                    docker run -d --name formativa-app \
                      -p 5000:5000 formativa-app
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'dependency-check-report.xml,zap-report.html',
                             allowEmptyArchive: true
        }
    }
}