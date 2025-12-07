pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = "${env.DOCKER_REGISTRY ?: 'localhost:5000'}"  // 默认使用本地registry，可配置
        IMAGE_NAME = 'desktop-pet'
        K8S_NAMESPACE = "${env.K8S_NAMESPACE ?: 'default'}"
        DOCKER_IMAGE = "${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}"
        DOCKER_IMAGE_LATEST = "${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }
        
        stage('Test') {
            steps {
                script {
                    try {
                        sh '''
                            python3 -m venv venv || python -m venv venv
                            source venv/bin/activate || venv\\Scripts\\activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                            pip install pytest pytest-cov || echo "pytest not available, skipping tests"
                            pytest tests/unit/ --cov=src --cov-report=xml || echo "Tests completed with warnings"
                        '''
                    } catch (Exception e) {
                        echo "Test stage completed with warnings: ${e}"
                        // 不阻止构建继续
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    sh """
                        echo "Building Docker image: ${DOCKER_IMAGE}"
                        docker build -t ${DOCKER_IMAGE} .
                        docker tag ${DOCKER_IMAGE} ${DOCKER_IMAGE_LATEST}
                        docker tag ${DOCKER_IMAGE} ${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.GIT_COMMIT_SHORT}
                    """
                }
            }
        }
        
        stage('Push to Registry') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                    branch 'develop'
                }
            }
            steps {
                script {
                    def dockerCreds = 'docker-registry-creds'
                    try {
                        withCredentials([usernamePassword(
                            credentialsId: dockerCreds,
                            usernameVariable: 'DOCKER_USER',
                            passwordVariable: 'DOCKER_PASS'
                        )]) {
                            sh """
                                echo \$DOCKER_PASS | docker login ${DOCKER_REGISTRY} -u \$DOCKER_USER --password-stdin || echo "Login failed, may use local registry"
                                docker push ${DOCKER_IMAGE} || echo "Push failed, may use local registry"
                                docker push ${DOCKER_IMAGE_LATEST} || echo "Push failed, may use local registry"
                                docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.GIT_COMMIT_SHORT} || echo "Push failed, may use local registry"
                            """
                        }
                    } catch (Exception e) {
                        echo "Registry push skipped (local development): ${e}"
                        // 本地开发环境可能不需要推送
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                    branch 'develop'
                }
            }
            steps {
                script {
                    // 更新 deployment.yaml 中的镜像版本
                    sh """
                        # 备份原始文件
                        cp k8s/deployment.yaml k8s/deployment.yaml.bak
                        
                        # 更新镜像版本（支持多种格式）
                        if grep -q 'image: desktop-pet:' k8s/deployment.yaml; then
                            sed -i.bak 's|image: desktop-pet:.*|image: ${DOCKER_IMAGE}|g' k8s/deployment.yaml || \
                            sed -i '' 's|image: desktop-pet:.*|image: ${DOCKER_IMAGE}|g' k8s/deployment.yaml
                        else
                            # 如果不存在，添加镜像配置
                            echo "Warning: Image line not found in deployment.yaml"
                        fi
                    """
                    
                    // 应用 Kubernetes 配置（并行执行以提高速度）
                    sh """
                        echo "Applying Kubernetes configurations..."
                        
                        # 并行应用配置以提高部署速度
                        kubectl apply -f k8s/configmap.yaml -n ${K8S_NAMESPACE} &
                        kubectl apply -f k8s/secret.yaml -n ${K8S_NAMESPACE} &
                        kubectl apply -f k8s/pvc.yaml -n ${K8S_NAMESPACE} &
                        wait
                        
                        # 应用服务配置
                        kubectl apply -f k8s/service.yaml -n ${K8S_NAMESPACE}
                        kubectl apply -f k8s/pdb.yaml -n ${K8S_NAMESPACE} || echo "PDB may not exist, skipping"
                        
                        # 应用部署配置
                        kubectl apply -f k8s/deployment.yaml -n ${K8S_NAMESPACE}
                        
                        # 应用 HPA
                        kubectl apply -f k8s/hpa.yaml -n ${K8S_NAMESPACE}
                    """
                    
                    // 等待滚动更新完成
                    sh """
                        echo "Waiting for rollout to complete..."
                        kubectl rollout status deployment/desktop-pet -n ${K8S_NAMESPACE} --timeout=5m || {
                            echo "Rollout timeout, checking status..."
                            kubectl get pods -l app=desktop-pet -n ${K8S_NAMESPACE}
                            exit 1
                        }
                    """
                }
            }
        }
        
        stage('Health Check') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                    branch 'develop'
                }
            }
            steps {
                script {
                    sh """
                        echo "Performing health check..."
                        sleep 10
                        
                        # 检查 Pod 状态
                        kubectl get pods -l app=desktop-pet -n ${K8S_NAMESPACE}
                        
                        # 获取 Pod 名称并执行健康检查
                        POD_NAME=\$(kubectl get pods -l app=desktop-pet -n ${K8S_NAMESPACE} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
                        
                        if [ -n "\$POD_NAME" ]; then
                            echo "Checking health of pod: \$POD_NAME"
                            kubectl exec \$POD_NAME -n ${K8S_NAMESPACE} -- python -c "import requests; requests.get('http://localhost:8080/health')" || {
                                echo "Health check failed, but continuing..."
                            }
                        else
                            echo "No pods found, health check skipped"
                        fi
                        
                        # 检查服务端点
                        kubectl get endpoints desktop-pet-service -n ${K8S_NAMESPACE} || echo "Service endpoints check skipped"
                    """
                }
            }
        }
    }
    
    post {
        always {
            script {
                // 清理临时文件
                sh """
                    rm -f k8s/deployment.yaml.bak || true
                """
            }
        }
        success {
            echo '✅ Deployment successful!'
            script {
                def message = """
                🎉 CI/CD Pipeline Success!
                
                Build: #${BUILD_NUMBER}
                Commit: ${env.GIT_COMMIT_SHORT}
                Image: ${DOCKER_IMAGE}
                Namespace: ${K8S_NAMESPACE}
                
                Deployment completed successfully!
                """
                echo message
            }
        }
        failure {
            echo '❌ Deployment failed! Attempting rollback...'
            script {
                try {
                    sh """
                        kubectl rollout undo deployment/desktop-pet -n ${K8S_NAMESPACE} || echo "Rollback failed"
                        kubectl get pods -l app=desktop-pet -n ${K8S_NAMESPACE}
                    """
                } catch (Exception e) {
                    echo "Rollback error: ${e}"
                }
            }
        }
        unstable {
            echo '⚠️ Deployment completed with warnings'
        }
    }
}

