pipeline {
    agent any

    environment {
        DOCKERHUB_USERNAME = 'inshirah1243'
        IMAGE_NAME = 'image-compressor'
    }

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://registry-1.docker.io', 'dockerhub-credentials') {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                bat '''
                    kubectl apply -f deployment.yaml
                    kubectl apply -f service.yaml
                    kubectl set image deployment/image-compressor-optimizer image-compressor-optimizer=inshirah1243/image-compressor:%BUILD_NUMBER%
                    kubectl rollout status deployment/image-compressor-optimizer
                '''
            }
        }
    }
}
