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
                    additionalArguments: '--scan requirements.txt --format XML --format HTML --out . --noupdate'
                )
                dependencyCheckPublisher(pattern: 'dependency-check-report.xml')

                script {
                    try {
                        sh '''
                            docker network create formativa-net || true
                            docker build -t formativa-app .
                            docker run -d --rm --name formativa-app \
                              --network formativa-net formativa-app
                            docker volume create zap-wrk || true
                            docker run --rm --network formativa-net \
                              -u 0 -v zap-wrk:/zap/wrk \
                              ghcr.io/zaproxy/zaproxy:stable \
                              zap-baseline.py \
                              -t http://formativa-app:5000 \
                              -r zap-report.html -I || true
                            docker run --rm -u 0 -v zap-wrk:/zap/wrk \
                              --volumes-from jenkins alpine \
                              cp -f /zap/wrk/zap-report.html "$WORKSPACE/zap-report.html" || true
                        '''
                    } finally {
                        sh '''
                            docker rm -f formativa-app >/dev/null 2>&1 || true
                            docker network rm formativa-net >/dev/null 2>&1 || true
                            docker volume rm -f zap-wrk >/dev/null 2>&1 || true
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
            archiveArtifacts artifacts: 'dependency-check-report.xml,dependency-check-report.html,zap-report.html',
                             allowEmptyArchive: true
        }
    }
}
