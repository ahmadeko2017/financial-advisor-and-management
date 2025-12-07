pipeline {
  agent any

  environment {
    IMAGE_NAME = "fintrack-api"
    IMAGE_TAG = "dev"
    FE_IMAGE_NAME = "fintrack-fe"
    FE_IMAGE_TAG = "dev"
    COMPOSE_PROJECT_NAME = "fintrack"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Backend') {
      steps {
        sh 'podman build -t ${IMAGE_NAME}:${IMAGE_TAG} -f backend/Dockerfile backend'
      }
    }

    stage('Unit Tests (podman run)') {
      steps {
        sh 'podman run --rm ${IMAGE_NAME}:${IMAGE_TAG} pytest'
      }
    }

    stage('Backend Lint') {
      steps {
        sh 'podman run --rm ${IMAGE_NAME}:${IMAGE_TAG} python -m compileall app'
      }
    }

    stage('Build Frontend') {
      steps {
        sh 'podman build -t ${FE_IMAGE_NAME}:${FE_IMAGE_TAG} -f frontend/Dockerfile frontend'
      }
    }

    stage('Frontend Lint') {
      steps {
        sh 'podman run --rm ${FE_IMAGE_NAME}:${FE_IMAGE_TAG} npm run lint'
      }
    }

    stage('Frontend Build Test') {
      steps {
        sh 'podman run --rm ${FE_IMAGE_NAME}:${FE_IMAGE_TAG} npm run build'
      }
    }

    stage('Smoke (podman compose)') {
      steps {
        sh '''
          export COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}
          podman compose -f docker-compose.yml up -d db redis
          podman run --rm --network ${COMPOSE_PROJECT_NAME}_default \\
            -e DATABASE_URL=postgresql+psycopg2://finuser:finpass@fintrack-db:5432/fintrack \\
            ${IMAGE_NAME}:${IMAGE_TAG} \\
            sh -c "python scripts/wait_for_db.py && python -m alembic -c alembic.ini upgrade head"
          podman run --rm --network ${COMPOSE_PROJECT_NAME}_default \\
            -e DATABASE_URL=postgresql+psycopg2://finuser:finpass@fintrack-db:5432/fintrack \\
            ${IMAGE_NAME}:${IMAGE_TAG} \\
            pytest tests/test_health.py
          podman compose -f docker-compose.yml down
        '''
      }
    }
  }

  post {
    always {
      sh '''
        export COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}
        podman compose -f docker-compose.yml down || true
        podman rmi ${IMAGE_NAME}:${IMAGE_TAG} || true
        podman rmi ${FE_IMAGE_NAME}:${FE_IMAGE_TAG} || true
      '''
    }
  }
}
