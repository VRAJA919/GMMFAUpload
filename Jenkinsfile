// Jenkins: GeoManager login + user-definition upload (Playwright Python).
//
// 1. Create credentials: kind "Username with password", ID: gm-mfa-upload-creds
//    (or change credentialsId below). Optional Secret Text for GM_OTP_CODE.
// 2. If you already export GM_USERNAME / GM_PASSWORD on the agent, you can remove
//    withCredentials and pass env only (see README). For PROD MFA without a static code,
//    set GM_OTP_EMAIL (Mailinator inbox) and MAILINATOR_DOMAIN=public on the agent or via withEnv.

pipeline {
    agent any

    parameters {
        booleanParam(name: 'RUN_E2E', defaultValue: true, description: 'Run Playwright tests against live GeoManager')
    }

    options {
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
    }

    environment {
        CI = 'true'
        PLAYWRIGHT_TIMEOUT_MS = '90000'
        PLAYWRIGHT_NAVIGATION_TIMEOUT_MS = '120000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv .venv 2>/dev/null || python -m venv .venv
                            . .venv/bin/activate
                            python -m pip install --upgrade pip
                            python -m pip install -r requirements.txt
                            python -m playwright install --with-deps chromium
                        '''
                    } else {
                        bat '''
                            python -m venv .venv
                            call .venv\\Scripts\\activate.bat
                            python -m pip install --upgrade pip
                            python -m pip install -r requirements.txt
                            python -m playwright install --with-deps chromium
                        '''
                    }
                }
            }
        }

        stage('Collect tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            . .venv/bin/activate
                            python -m pytest --collect-only -q
                        '''
                    } else {
                        bat '''
                            call .venv\\Scripts\\activate.bat
                            python -m pytest --collect-only -q
                        '''
                    }
                }
            }
        }

        stage('E2E') {
            when {
                expression { return params.RUN_E2E }
            }
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'gm-mfa-upload-creds',
                        usernameVariable: 'GM_USERNAME',
                        passwordVariable: 'GM_PASSWORD'
                    )
                ]) {
                    script {
                        if (isUnix()) {
                            sh '''
                                . .venv/bin/activate
                                python -m pytest tests/ -v --alluredir=allure-results --tb=short
                            '''
                        } else {
                            bat '''
                                call .venv\\Scripts\\activate.bat
                                python -m pytest tests/ -v --alluredir=allure-results --tb=short
                            '''
                        }
                    }
                }
            }
        }
    }

    post {
        failure {
            archiveArtifacts artifacts: 'allure-results/**/*', allowEmptyArchive: true
        }
    }
}
