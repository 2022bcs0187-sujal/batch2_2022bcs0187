pipeline {
    agent any

    environment {
        DOCKERHUB_CREDS = credentials('dockerhub-creds')
        BEST_ACCURACY   = credentials('best-accuracy')
        IMAGE_NAME      = '2022bcs0187sujal/batch2_2022bcs0187'
        DOCKER_AVAILABLE = 'false'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                    if command -v python3 >/dev/null 2>&1; then
                      PY=python3
                    elif command -v python >/dev/null 2>&1; then
                      PY=python
                    elif command -v apt-get >/dev/null 2>&1; then
                      SUDO=''
                      if [ "$(id -u)" -ne 0 ]; then
                        if command -v sudo >/dev/null 2>&1; then
                          SUDO=sudo
                        else
                          echo "ERROR: Python is not installed and sudo is unavailable." >&2
                          exit 1
                        fi
                      fi
                      $SUDO apt-get update
                      $SUDO apt-get install -y python3 python3-venv python3-pip
                      PY=python3
                    else
                      echo "ERROR: Python is not installed on this node." >&2
                      exit 1
                    fi
                    $PY -m venv venv
                    . venv/bin/activate
                    $PY -m pip install --upgrade pip
                    $PY -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
                '''
            }
        }

        stage('Detect Docker') {
            steps {
                script {
                    env.DOCKER_AVAILABLE = sh(script: 'if command -v docker >/dev/null 2>&1; then echo true; else echo false; fi', returnStdout: true).trim()
                    echo "Docker available: ${env.DOCKER_AVAILABLE}"
                }
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                    if command -v python3 >/dev/null 2>&1; then
                      PY=python3
                    elif command -v python >/dev/null 2>&1; then
                      PY=python
                    else
                      echo "ERROR: Python is not installed on this node." >&2
                      exit 1
                    fi
                    . venv/bin/activate
                    $PY scripts/train.py
                    mkdir -p app/artifacts
                    cp output/results/results.json app/artifacts/metrics.json
                '''
            }
        }

        stage('Read Accuracy') {
            steps {
                script {
                    def metrics = readJSON file: 'app/artifacts/metrics.json'
                    env.CURRENT_ACCURACY = metrics.accuracy.toString()
                    echo "Current Accuracy: ${env.CURRENT_ACCURACY}"
                }
            }
        }

        stage('Compare Accuracy') {
            steps {
                script {
                    env.IS_BETTER = 'false'
                    if (env.CURRENT_ACCURACY.toFloat() > BEST_ACCURACY.toFloat()) {
                        env.IS_BETTER = 'true'
                        echo 'New model is better'
                    } else {
                        echo 'New model is NOT better'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when {
                allOf {
                    expression { env.IS_BETTER == 'true' }
                    expression { env.DOCKER_AVAILABLE == 'true' }
                }
            }
            steps {
                sh '''
                    echo $DOCKERHUB_CREDS_PSW | docker login \
                    -u $DOCKERHUB_CREDS_USR --password-stdin
                    docker build -t $IMAGE_NAME:latest .
                '''
            }
        }

        stage('Push Docker Image') {
            when {
                allOf {
                    expression { env.IS_BETTER == 'true' }
                    expression { env.DOCKER_AVAILABLE == 'true' }
                }
            }
            steps {
                sh 'docker push $IMAGE_NAME:latest'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'app/artifacts/**', fingerprint: true
        }
    }
}
