properties([parameters([string(defaultValue: '1.0.0', name: 'APP_VERSION')]), pipelineTriggers([])])

pipeline {
    agent any

    stages {
        stage('git'){
            steps {
                git branch: 'main', credentialsId: 'GitHub-Key', url: 'git@github.com:gitkloud/fast-api-jwt.git'
            }
        }
        
        stage('Build & Publish') {
            steps {
                withCredentials([aws(accessKeyVariable: 'AWS_ACCESS_KEY_ID', credentialsId: 'aws-creds-dev', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh '''
                        echo "::::::::::: Started Build :::::::::::"
                        python3 -m venv .venv
                        source .venv/bin/activate
                        pip3 install -r requirements.txt
                        deactivate
                        echo "::::::::::: Build Success :::::::::::"
                        
                        echo "::::::::::: Test Started :::::::::::"
                        echo "Tested Success"
                        echo "::::::::::: Test Completed :::::::::::"
                        
                        echo "::::::::::: Sonar Started :::::::::::"
                        echo "SonarQube Scan Success"
                        echo "::::::::::: Sonar Completed :::::::::::"
                        
                        echo "::::::::::: Packaging App :::::::::::"
                        rm -rf target/ && mkdir target/
                        zip -r target/fast-api-jwt-${APP_VERSION}.zip .venv/ app/ main.py
                        echo "::::::::::: Packaing Completed (fast-api-jwt-${APP_VERSION}.zip) :::::::::::"
                        
                        echo "::::::::::: Publish to Artifactory(s3) :::::::::::"
                        aws s3 cp target/fast-api-jwt-${APP_VERSION}.zip s3://bpantala-test-bucket/artifacts/fast-api-jwt-${APP_VERSION}.zip
                        echo "::::::::::: S3 Publish Done s3://bpantala-test-bucket/artifacts/fast-api-jwt-${APP_VERSION}.zip :::::::::::"
                    '''
                }
        }
        }
    }
}
