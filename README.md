# M1 Project

🌈 Run algorithms on real Quantum Computers:

[m1.ogoro.me](https://m1.ogoro.me/)

---

M1 is a complete web application using:

<a id="my-anchor"></a>

- [Flask](https://flask.palletsprojects.com/) web framework on [Gunicorn](https://gunicorn.org/) WSGI server
- Quantum computation on real devices with [IBM Qiskit](https://qiskit.org/)
- Docker containers in [AWS ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html) cluster
- Automated infrastructure with [AWS Cloudformation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html)
- User management with [AWS Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html)
- Facebook login with [OAuth flow](https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow)
- Telegram bot with [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- Multi-process and multi-threaded tasks, queue and execution
- 100% [Pytest](https://docs.pytest.org/) [Coverage](https://coverage.readthedocs.io/)

---

- 100% of AWS infrastructure is automatically deployed
- 78 AWS Resources in 8 Cloudformation Stacks
- 150 unit and integration tests

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
