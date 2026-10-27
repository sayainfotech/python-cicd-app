pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        APP_NAME = 'python-cicd-app'
        K8S_NAMESPACE = 'default'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

       stage('Install Dependencies') {
    steps {
        sh '''
            set -e

            python3 --version

            rm -rf .venv

            python3 -m venv .venv

            .venv/bin/python -m pip install --upgrade pip

            .venv/bin/python -m pip install -r requirements.txt
        '''
    }
}

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner
                        """
                    }
                }
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        set -eu

                        IMAGE="$DOCKER_USER/$APP_NAME:$BUILD_NUMBER"

                        echo "$DOCKER_PASSWORD" |
                            docker login \
                            --username "$DOCKER_USER" \
                            --password-stdin

                        docker build -t "$IMAGE" .
                        docker push "$IMAGE"

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        set -eu

                        IMAGE="$DOCKER_USER/$APP_NAME:$BUILD_NUMBER"

                        sed "s|IMAGE_PLACEHOLDER|$IMAGE|g" \
                            k8s/deployment.yaml \
                            > k8s/deployment-rendered.yaml

                        kubectl apply -n "$K8S_NAMESPACE" \
                            -f k8s/deployment-rendered.yaml

                        kubectl apply -n "$K8S_NAMESPACE" \
                            -f k8s/service.yaml

                        kubectl rollout status \
                            deployment/python-cicd-app \
                            -n "$K8S_NAMESPACE" \
                            --timeout=180s

                        kubectl get pods -n "$K8S_NAMESPACE"
                        kubectl get svc -n "$K8S_NAMESPACE"

                        rm -f k8s/deployment-rendered.yaml
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the stage logs.'
        }

        always {
            deleteDir()
        }
    }
}
