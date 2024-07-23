pipeline {
    agent any

    environment {
        VENV_PATH = 'venv'
        FLASK_APP = 'SSDPrac/flask/app.py'  // Correct path to the Flask app
        PATH = "$VENV_PATH/bin:$PATH"
        SONARQUBE_SCANNER_HOME = tool name: 'SonarQube Scanner'
        DEPENDENCY_CHECK_HOME = tool name: 'OWASP Dependency-Check Vulnerabilities'
    }

    stages {
        stage('Check Docker') {
            steps {
                sh 'docker --version'
            }
        }

        stage('Clone Repository') {
            steps {
                dir('workspace') {
                    git branch: 'main', url: 'https://github.com/claudichee/SSDPrac'
                }
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                dir('workspace/flask') {
                    sh 'python3 -m venv $VENV_PATH'
                }
            }
        }

        stage('Activate Virtual Environment and Install Dependencies') {
            steps {
                dir('workspace/flask') {
                    sh '. $VENV_PATH/bin/activate && pip install -r requirements.txt'
                }
            }
        }

        stage('Debug Dependency-Check Path') {
            steps {
                script {
                    echo "Dependency-Check Home: ${DEPENDENCY_CHECK_HOME}"
                    sh 'ls -la ${DEPENDENCY_CHECK_HOME}/bin'
                }
            }
        }

        stage('OWASP DependencyCheck') {
            steps {
                withCredentials([string(credentialsId: 'NVD_API_KEY', variable: 'NVD_API_KEY')]) {
                    script {
                        def nvdApiKey = env.NVD_API_KEY
                        sh """
                            ${DEPENDENCY_CHECK_HOME}/bin/dependency-check.sh \\
                            --project "My Project" \\
                            --scan . \\
                            --format XML \\
                            --out dependency-check-report.xml \\
                            --noupdate \\
                            --cveValidForHours 0 \\
                            --cveUrlBase "https://nvd.nist.gov/feeds/xml/cve/nvdcve-2.0-" \\
                            --cveUrlModified "https://nvd.nist.gov/feeds/xml/cve/nvdcve-2.0-Modified.xml.gz" \\
                            --data ${DEPENDENCY_CHECK_HOME}/data \\
                            --nvdApiKey ${nvdApiKey}
                        """
                    }
                }
            }
        }

        stage('UI Testing') {
            steps {
                script {
                    // Start the Flask app in the background
                    sh '. $VENV_PATH/bin/activate && FLASK_APP=$FLASK_APP flask run &'
                    // Give the server a moment to start
                    sh 'sleep 5'
                    // Debugging: Check if the Flask app is running
                    sh 'curl -s http://127.0.0.1:5000 || echo "Flask app did not start"'

                    // Test a strong password
                    sh '''
                    curl -s -X POST -F "password=ThisIsStrongPassword123" http://127.0.0.1:5000 | grep "Welcome"
                    '''

                    // Test a weak password
                    sh '''
                    curl -s -X POST -F "password=password123" http://127.0.0.1:5000 | grep "Password does not meet the requirements"
                    '''

                    // Stop the Flask app
                    sh 'pkill -f "flask run"'
                }
            }
        }

        stage('Integration Testing') {
            steps {
                dir('workspace/flask') {
                    sh '. $VENV_PATH/bin/activate && pytest --junitxml=integration-test-results.xml'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('workspace/flask') {
                    sh 'docker build -t flask-app .'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        dir('workspace/flask') {
                            sh '''
                            ${SONARQUBE_SCANNER_HOME}/bin/sonar-scanner \\
                            -Dsonar.projectKey=flask-app \\
                            -Dsonar.sources=. \\
                            -Dsonar.inclusions=app.py \\
                            -Dsonar.host.url=http://sonarqube:9000 \\
                            -Dsonar.login=${SONARQUBE_TOKEN}
                            '''
                        }
                    }
                }
            }
        }

        stage('Deploy Flask App') {
            steps {
                script {
                    echo 'Deploying Flask App...'
                    // Stop any running container on port 5000
                    sh 'docker ps --filter publish=5000 --format "{{.ID}}" | xargs -r docker stop'
                    // Remove the stopped container
                    sh 'docker ps -a --filter status=exited --filter publish=5000 --format "{{.ID}}" | xargs -r docker rm'
                    // Run the new Flask app container
                    sh 'docker run -d -p 5000:5000 flask-app'
                    sh 'sleep 10'
                }
            }
        }
    }

    post {
        failure {
            script {
                echo 'Build failed, not deploying Flask app.'
            }
        }
        always {
            archiveArtifacts artifacts: 'workspace/flask/dependency-check-report.xml', allowEmptyArchive: true
            archiveArtifacts artifacts: 'workspace/flask/integration-test-results.xml', allowEmptyArchive: true
        }
    }
}
