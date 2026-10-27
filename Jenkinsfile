
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        APP_NAME       = 'python-cicd-app'
        DOCKERHUB_USER = 'abhisheksaya5'
        K8S_NAMESPACE  = 'default'
        MANIFEST_REPO  = 'https://github.com/sayainfotech/application-manifest.git'
        MANIFEST_BRANCH = 'main'
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
                    set -eu

                    python3 --version

                    rm -rf .venv

                    python3 -m venv .venv

                    .venv/bin/python -m pip install --upgrade pip

                    .venv/bin/python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    set -eu

                    .venv/bin/python -m pytest -v \
                        --junitxml=test-results.xml
                '''
            }

            post {
                always {
                    junit(
                        testResults: 'test-results.xml',
                        allowEmptyResults: true
                    )
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('SonarQube') {
                        sh """
                            set -eu

                            test -f "\$WORKSPACE/sonar-project.properties"

                            "${scannerHome}/bin/sonar-scanner" \
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

                        echo "Building image: $IMAGE"

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

        stage('Update GitOps Manifest') {
            steps {
                dir('manifests') {
                    git(
                        branch: "${MANIFEST_BRANCH}",
                        url: "${MANIFEST_REPO}"
                    )

                    withCredentials([
                        usernamePassword(
                            credentialsId: 'github-manifest-write',
                            usernameVariable: 'GITHUB_USER',
                            passwordVariable: 'GITHUB_TOKEN'
                        )
                    ]) {
                        sh '''
                            set -eu

                            IMAGE="$DOCKERHUB_USER/$APP_NAME:$BUILD_NUMBER"

                            echo "Updating GitOps image to: $IMAGE"

                            test -f deployment.yaml

                            # Update the image field in deployment.yaml.
                            # This assumes the manifest has one container
                            # image line that should be replaced.
                            sed -i \
                                '/^[[:space:]]*image:/s|image:.*|image: '"$IMAGE"'|' \
                                deployment.yaml

                            echo "Checking the updated image:"
                            grep -n 'image:' deployment.yaml

                            git config user.name "Jenkins CI"
                            git config user.email "jenkins@example.com"

                            git add deployment.yaml

                            if git diff --cached --quiet; then
                                echo "No manifest changes detected."
                                exit 1
                            fi

                            git commit -m \
                                "Update python-cicd-app image to ${BUILD_NUMBER}"

                            # Authenticate only for this Git push.
                            AUTH=$(printf '%s:%s' \
                                "$GITHUB_USER" "$GITHUB_TOKEN" |
                                base64 -w 0)

                            git \
                                -c http.extraheader="AUTHORIZATION: basic $AUTH" \
                                push origin HEAD:main

                            unset AUTH GITHUB_TOKEN
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo '''
            CI pipeline completed successfully!

            Docker image pushed to Docker Hub.
            GitOps manifest updated in GitHub.
            Argo CD should now detect the Git change and synchronize
            the application to Minikube, provided automated sync is enabled.
            '''
        }

        failure {
            echo '''
            Pipeline failed.
            Open Console Output and inspect the first failed stage.
            '''
        }

        always {
            deleteDir()
        }
    }
}
