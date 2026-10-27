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
                    set -eu

                    echo "Current workspace:"
                    pwd

                    echo "Checking SonarQube configuration..."
                    test -f "\$WORKSPACE/sonar-project.properties"

                    echo "Starting SonarQube analysis..."
                    ${scannerHome}/bin/sonar-scanner \
                        -Dproject.settings="\$WORKSPACE/sonar-project.properties"
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
        dir('manifests') {
            git branch: 'main',
                url: 'https://github.com/sayainfotech/application-manifest.git'

            sh '''
                set -eu

                IMAGE="$DOCKER_USER/python-cicd-app:$BUILD_NUMBER"

                echo "Checking manifest files..."
                test -f deployment.yaml
                test -f service.yaml

                echo "Updating image to: $IMAGE"
                sed "s|IMAGE_PLACEHOLDER|$IMAGE|g" \
                    deployment.yaml > deployment-rendered.yaml

                echo "Applying deployment..."
                kubectl apply -n "$K8S_NAMESPACE" \
                    -f deployment-rendered.yaml

                echo "Applying service..."
                kubectl apply -n "$K8S_NAMESPACE" \
                    -f service.yaml

                echo "Waiting for rollout..."
                kubectl rollout status \
                    deployment/python-cicd-app \
                    -n "$K8S_NAMESPACE" \
                    --timeout=180s

                kubectl get deployments -n "$K8S_NAMESPACE"
                kubectl get pods -n "$K8S_NAMESPACE"
                kubectl get svc -n "$K8S_NAMESPACE"
            '''
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
