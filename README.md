## M1 Project

🌈 Run algorithms on real Quantum Computers:

[m1.ogoro.me](https://m1.ogoro.me/)

M1 is complete web application using:

<a id="my-anchor"></a>



- Flask web framework on Gunicorn WSGI server
- Docker container
- AWS infrastructure with Cloudformation CDK
- 100% Pytest Coverage

- 150 unit and integration tests
- 100% of AWS infrastructure is automatically deployed
- 78 AWS Resources in 8 Cloudformation Stacks

[Top](#m1-project)

Using:

Python:
- Flask
- Qiskit

CloudFormation:
- VPC, EC2, ELB, S3
- Subnets, Endpoints
- Security Groups
- IAM
- CloudWatch
- DynamoDB

- Boto3 Python SDK
- Cloud9 IDE

API:
- API Gateway
- OpenAPI Swagger YAML
- Cognito
- JWT tokens

CDN:
- Cloudfront
- Route53
- Custom domain
- ACM SSL Certificate

Container build:
- Docker
- ECR

Container deploy:
- ECS
- Fargate
- Container EC2 Instance

CI/CD:
- CodePipeline
- CodeCommit
- CodeBuild
