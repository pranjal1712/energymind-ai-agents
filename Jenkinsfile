pipeline {
    agent any

    environment {
        APP_NAME = "energymind-app"
        IMAGE_NAME = "energymind-app:latest"
        K8S_DEPLOYMENT = "k8s/deployment.yaml"
        K8S_SERVICE = "k8s/service.yaml"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/pranjal1712/energymind-ai-agents.git'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME} .'
            }
        }

        stage('K3s Import') {
            steps {
                sh 'sudo k3s ctr images import <(docker save ${IMAGE_NAME}) || true'
            }
        }

        stage('Deploy to K8s') {
            steps {
                sh 'kubectl apply -f ${K8S_DEPLOYMENT}'
                sh 'kubectl apply -f ${K8S_SERVICE}'
            }
        }
        
        stage('Verify') {
            steps {
                sh 'kubectl get pods'
                sh 'kubectl get svc'
            }
        }
    }
}
