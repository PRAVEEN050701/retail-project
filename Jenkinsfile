pipeline {

agent any

parameters {

    choice(
        name: 'DEPLOYMENT_ACTION',
        choices: ['DEPLOY', 'ROLLBACK'],
        description: 'Choose deployment action'
    )

    choice(
        name: 'ENVIRONMENT',
        choices: ['UAT', 'PRODUCTION'],
        description: 'Choose target environment'
    )

    string(
        name: 'VERSION',
        defaultValue: '4.2.1',
        description: 'Version to deploy'
    )

    choice(
        name: 'CONFIRM_PROD',
        choices: ['NO', 'YES'],
        description: 'Confirm production deployment'
    )
}

environment {

    IMAGE_NAME = 'retail-project'
    PROD_CONTAINER = 'retail-project-prod'
    NEW_CONTAINER = 'retail-project-new'
    NETWORK_NAME = 'retail-network'

    HOST_PORT = '8094'
    CONTAINER_PORT = '8081'

    GIT_EXE = 'C:/Program Files/Git/cmd/git.exe'
}

stages {

    stage('Validate Parameters') {

        steps {

            script {

                echo '======================================'
                echo 'DEPLOYMENT CONFIGURATION'
                echo '======================================'

                echo "Action      : ${params.DEPLOYMENT_ACTION}"
                echo "Environment : ${params.ENVIRONMENT}"
                echo "Version     : ${params.VERSION}"
                echo "Confirm Prod: ${params.CONFIRM_PROD}"

                echo '======================================'

                if (
                    params.ENVIRONMENT == 'PRODUCTION' &&
                    params.CONFIRM_PROD != 'YES'
                ) {

                    error(
                        'PRODUCTION deployment requires CONFIRM_PROD = YES'
                    )
                }
            }
        }
    }


    stage('Validate Git Tag') {

        when {

            expression {
                params.DEPLOYMENT_ACTION == 'DEPLOY'
            }
        }

        steps {

            bat """
                "${GIT_EXE}" fetch --tags --force
                "${GIT_EXE}" rev-parse --verify refs/tags/v${params.VERSION}
            """
        }
    }


    stage('Identify Commit') {

        when {

            expression {
                params.DEPLOYMENT_ACTION == 'DEPLOY'
            }
        }

        steps {

            script {

                def commit = bat(
                    script: """
                        "${GIT_EXE}" rev-list -n 1 v${params.VERSION}
                    """,
                    returnStdout: true
                ).trim()

                echo "Selected commit: ${commit}"

                env.DEPLOY_COMMIT = commit
            }
        }
    }


    stage('Check Tools') {

        steps {

            echo 'Checking Git...'

            bat """
                "${GIT_EXE}" --version
            """

            echo 'Checking Docker...'

            bat 'docker --version'
        }
    }


    stage('Build Docker Image') {

        when {

            expression {
                params.DEPLOYMENT_ACTION == 'DEPLOY'
            }
        }

        steps {

            echo "Building ${IMAGE_NAME}:${params.VERSION}"

            bat """
                docker build -t ${IMAGE_NAME}:${params.VERSION} .
            """
        }
    }


    stage('Verify Docker Image') {

        when {

            expression {
                params.DEPLOYMENT_ACTION == 'DEPLOY'
            }
        }

        steps {

            bat """
                docker image inspect ${IMAGE_NAME}:${params.VERSION}
            """
        }
    }


    stage('Create Network') {

        when {

            expression {
                params.DEPLOYMENT_ACTION == 'DEPLOY'
            }
        }

        steps {

            bat """
                docker network inspect ${NETWORK_NAME} >nul 2>&1 || docker network create ${NETWORK_NAME}
            """
        }
    }


    stage('Record Previous Production Image') {

        when {

            expression {
                params.DEPLOYMENT_ACTION == 'DEPLOY'
            }
        }

        steps {

            script {

                def containerExists = bat(
                    script: """
                        docker inspect ${PROD_CONTAINER} >nul 2>&1
                    """,
                    returnStatus: true
                )

                if (containerExists == 0) {

                    def oldImage = bat(
                        script: """
                            docker inspect ${PROD_CONTAINER} --format="{{.Config.Image}}"
                        """,
                        returnStdout: true
                    ).trim()

                    env.OLD_IMAGE = oldImage

                    echo "OLD PRODUCTION IMAGE: ${env.OLD_IMAGE}"

                } else {

                    echo 'No existing production container found.'
                }
            }
        }
    }


    stage('Stop Old Production') {

        when {

            expression {
                params.DEPLOYMENT_ACTION == 'DEPLOY'
            }
        }

        steps {

            bat """
                docker rm -f ${PROD_CONTAINER} >nul 2>&1 || exit /b 0
            """

            echo 'Old production container stopped.'
        }
    }


    stage('Start New Version') {

        when {

            expression {
                params.DEPLOYMENT_ACTION == 'DEPLOY'
            }
        }

        steps {

            echo "NEW VERSION: ${IMAGE_NAME}:${params.VERSION}"

            bat """
                docker rm -f ${NEW_CONTAINER} >nul 2>&1 || exit /b 0

                docker run -d ^
                --name ${NEW_CONTAINER} ^
                --network ${NETWORK_NAME} ^
                -p ${HOST_PORT}:${CONTAINER_PORT} ^
                -e APP_VERSION=${params.VERSION} ^
                -e APP_ENV=${params.ENVIRONMENT} ^
                -e PAYMENT_STATUS=FIXED ^
                ${IMAGE_NAME}:${params.VERSION}
            """
        }
    }


    stage('Health Check') {

        when {

            expression {
                params.DEPLOYMENT_ACTION == 'DEPLOY'
            }
        }

        steps {

            script {

                echo 'Checking application health...'

                def healthResult = powershell(
                script: """
                    try {
                        Invoke-WebRequest -Uri "http://localhost:${HOST_PORT}/health" -UseBasicParsing
                        exit 0
                    }
                    catch {
                        exit 1
                    }
                """,
                returnStatus: true
            )


                if (healthResult != 0) {

                    echo 'HEALTH CHECK FAILED'

                    error(
                        'New version failed health check'
                    )
                }

                echo 'HEALTH CHECK PASSED'
            }
        }
    }


    stage('Complete Deployment') {

        when {

            expression {
                params.DEPLOYMENT_ACTION == 'DEPLOY'
            }
        }

        steps {

            script {

                echo "OLD VERSION: ${env.OLD_IMAGE}"
                echo "NEW VERSION: ${IMAGE_NAME}:${params.VERSION}"

                bat """
                    docker rename ${NEW_CONTAINER} ${PROD_CONTAINER}
                """

                echo 'FINAL STATE: DEPLOYMENT SUCCESSFUL'
            }
        }
    }
}


post {

    failure {

        script {

            echo '======================================'
            echo 'DEPLOYMENT FAILED'
            echo 'STARTING AUTOMATIC ROLLBACK'
            echo '======================================'


            bat """
                docker rm -f ${NEW_CONTAINER} >nul 2>&1 || exit /b 0
            """


            if (env.OLD_IMAGE) {

                echo "RESTORING OLD IMAGE: ${env.OLD_IMAGE}"


                bat """
                    docker rm -f ${PROD_CONTAINER} >nul 2>&1 || exit /b 0

                    docker run -d ^
                    --name ${PROD_CONTAINER} ^
                    --network ${NETWORK_NAME} ^
                    -p ${HOST_PORT}:${CONTAINER_PORT} ^
                    -e APP_ENV=PRODUCTION ^
                    -e PAYMENT_STATUS=FIXED ^
                    ${env.OLD_IMAGE}
                """


                def rollbackHealth = bat(
                    script: """
                        curl.exe -f http://localhost:${HOST_PORT}/health
                    """,
                    returnStatus: true
                )


                if (rollbackHealth == 0) {

                    echo 'ROLLBACK HEALTH CHECK PASSED'
                    echo 'FINAL STATE: ROLLBACK VERIFIED'

                } else {

                    echo 'ROLLBACK HEALTH CHECK FAILED'

                    error(
                        'ROLLBACK FAILED'
                    )
                }

            } else {

                echo 'No previous image found.'
                echo 'FINAL STATE: ROLLBACK REQUIRED'
            }
        }
    }


    success {

        echo '======================================'
        echo 'PIPELINE COMPLETED SUCCESSFULLY'
        echo '======================================'
    }
}


}
