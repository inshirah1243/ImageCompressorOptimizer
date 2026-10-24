pipeline {
    agent any

    environment {
        // Replace this placeholder with your Docker Hub username.
        DOCKERHUB_USERNAME = 'DOCKERHUB_USERNAME'
        IMAGE_NAME = 'image-compressor-optimizer'
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
                    // Create this Jenkins Username/Password credential with ID: docker-hub-credentials
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-credentials') {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                // Create this Jenkins Secret file credential with ID: kubeconfig-file.
                withCredentials([file(credentialsId: 'kubeconfig-file', variable: 'KUBECONFIG')]) {
                    sh '''
                        kubectl apply -f deployment.yaml
                        kubectl apply -f service.yaml
                        kubectl set image deployment/image-compressor-optimizer \\
                          image-compressor-optimizer=${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${BUILD_NUMBER}
                        kubectl rollout status deployment/image-compressor-optimizer
                    '''
                }
            }
        }
    }
}
