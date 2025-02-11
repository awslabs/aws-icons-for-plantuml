workspace {

    model {
        user = person "User" {
            tags "User"
        }
        softwareSystem = softwareSystem "Video Transcription Service" {
           
            s3bucket = container "Amazon S3 bucket" {
                tags "SimpleStorageServiceBucket"

                user -> this "Uploads"
            }

            objectcreated = container "ObjectCreated event handler" "" "AWS Lambda function" {
                tags "LambdaLambdaFunction"

                component "Boto3" "AWS SDK for Python" {
                    technology "Python package"
                    url https://aws.amazon.com/sdk-for-python/
                }
                
                s3bucket -> this "ObjectCreated event"
            }

            stepfunction = container "transcribe workflow" "" "Step Functions workflow" {
                tags "StepFunctions"

                objectcreated -> this
            }

            extractaudio = container "extract audio" "" "AWS Lambda function" {
                tags "LambdaLambdaFunction"

                component "Boto3" "AWS SDK for Python" {
                    technology "Python package"
                    url https://aws.amazon.com/sdk-for-python/
                }

                stepfunction -> this "step 1"
            }

            mediaconvert = container "AWS Elemental MediaConvert" {
                tags "ElementalMediaConvert"

                extractaudio -> this "create job"
                this -> s3bucket "save audio"
            }

            transcribeaudio = container "transcribe audio" "" "AWS Lambda function" {
                tags "LambdaLambdaFunction"

                component "Boto3" "AWS SDK for Python" {
                    technology "Python package"
                    url https://aws.amazon.com/sdk-for-python/
                }

                stepfunction -> this "step 2"
            }

            transcribe = container "Amazon Transcribe" {
                tags "Transcribe"

                transcribeaudio -> this "start transcription job"
                this -> s3bucket "save transcription"
            }



        }

        live = deploymentEnvironment "Live" {
            deploymentNode "Amazon Web Services" {
                tags "AWSCloud"
                
                deploymentNode "us-east-1" {
                    tags "Region"

                    deploymentNode "Amazon S3" {
                        tags "SimpleStorageService"

                        containerInstance s3bucket
                    }

                    deploymentNode "AWS Step Functions" {
                        tags "StepFunctions"

                        containerInstance extractaudio
                        containerInstance transcribeaudio
                    }

                    infrastructureNode "AWS Elemental MediaConvert" {
                        tags "ElementalMediaConvert"
                    }

                    infrastructureNode "Amazon Transcribe" {
                        tags "Transcribe"
                    }                 
                }
            }
        }
    }

    views {
        styles {
            element "Person" {
                shape Person
            }
        }

        systemContext softwareSystem "SystemContext" {
            include *
            autoLayout
        }

        container softwareSystem {
            include *
            autolayout lr
        }

        component objectcreated {
            include *
            autoLayout lr
        }

        deployment softwareSystem live {
            include *
            autoLayout lr
        }

        theme https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v20.0/dist/aws-icons-structurizr-theme.json
    }

}