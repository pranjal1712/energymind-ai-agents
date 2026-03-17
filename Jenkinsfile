pipeline {
    agent any

    environment {
        IMAGE_NAME = "energymind-app:latest"
        CONTAINER_NAME = "energymind-container"
    }

    stages {
        stage('Docker Build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME} .'
            }
        }

        stage('Docker Run') {
            steps {
                // Stop and remove existing container if it exists
                sh '''
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} -p 8501:7860 -p 8000:8000 ${IMAGE_NAME}
                '''
            }
        }

        stage('Verify') {
            steps {
                sh 'docker ps'
            }
        }
    }
}
