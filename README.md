### Cloudformation Stacks:

[Core stack](stack-templates/m1-core-stack.yml):

VPC, EC2, S3, ELB, AMI, Subnets, Routes, Custom NAT Instances 

[Cluster stack](stack-templates/m1-cluster-stack.yml):

ECR, ECS, Fargate, Cluster EC2, ASG, IAM Roles, CloudWatch

[DNS stack](stack-templates/m1-dns-stack.yml):

Route 53, ACM Certificate, Cloudfront

[API stack](stack-templates/m1-api-stack.yml):

API Gateway, VPC Link


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
- Frontend with [Bootstrap](https://getbootstrap.com/docs/4.6/getting-started/introduction/)
- API with [AWS API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html) and [Swagger](https://swagger.io/)
- 100% [Pytest](https://docs.pytest.org/) [Coverage](https://coverage.readthedocs.io/)

---

- 100% of AWS infrastructure is automatically deployed
- 78 AWS Resources in 8 Cloudformation Stacks
- 
-
- 150 unit and integration tests

[Top](#m1-project)



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
