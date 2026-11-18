// MIDTERM-FA23-BDS-025 : GitHub push -> retrain -> test -> Docker build -> redeploy on EC2 -> email
pipeline {
    agent any
    triggers {
        githubPush()          // started by the GitHub webhook, no manual build needed
    }
    options {
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15'))
    }
    environment {
        STUDENT_ID = 'FA23-BDS-025'
        IMAGE      = 'masharibkhan/midterm-fa23-bds-025'
        CONTAINER  = 'midterm-app'
        APP_PORT   = '8000'
        NOTIFY_TO  = 'qasimalik@gmail.com'
    }
    stages {
        stage('Fetch latest data') {
            steps {
                sh '''
                    git log -1 --pretty="commit %H%nauthor %an%ndate   %ad%n%s"
                    echo "dataset rows (incl. header): $(wc -l < dataset/train.csv)"
                '''
            }
        }
        stage('Set up Python') {
            steps {
                sh '''
                    [ -d .venv ] || python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -q --upgrade pip
                    pip install -q -r requirements.txt
                    pip freeze > requirements.lock      # exact versions for the Docker image
                    pip install -q -r requirements-dev.txt
                '''
            }
        }
        stage('Train') {
            steps {
                sh '''
                    . .venv/bin/activate
                    rm -rf artifacts
                    GIT_COMMIT=$(git rev-parse HEAD) python train.py
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m pytest -q tests
                '''
            }
        }
        stage('Build Docker image') {
            steps {
                sh 'docker build -t $IMAGE:$BUILD_NUMBER -t $IMAGE:latest .'
            }
        }
        stage('Deploy on EC2') {
            steps {
                sh '''
                    docker rm -f $CONTAINER 2>/dev/null || true
                    docker run -d --name $CONTAINER --restart unless-stopped \
                        -p $APP_PORT:8000 $IMAGE:$BUILD_NUMBER
                    for i in $(seq 1 30); do
                        if curl -fs http://localhost:$APP_PORT/metrics; then echo; echo "Deployed OK"; exit 0; fi
                        sleep 2
                    done
                    echo "App did not come up"; docker logs $CONTAINER; exit 1
                '''
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'artifacts/metrics.json', allowEmptyArchive: true
            script {
                def metrics = fileExists('artifacts/metrics.json') ? readFile('artifacts/metrics.json') : 'metrics not available'
                def sha = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                mail(
                    to: env.NOTIFY_TO,
                    bcc: 'asharib.mk@gmail.com',
                    subject: "${env.STUDENT_ID} | ${env.JOB_NAME} #${env.BUILD_NUMBER} | ${currentBuild.currentResult}",
                    body: """Student Reg No: ${env.STUDENT_ID}
Job: ${env.JOB_NAME}  Build: #${env.BUILD_NUMBER}
Result: ${currentBuild.currentResult}
Commit: ${sha}
Build URL: ${env.BUILD_URL}

Metrics:
${metrics}
"""
                )
            }
        }
    }
}
