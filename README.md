## M1 Project

🌈 Run algorithms on real Quantum Computers:

[m1.ogoro.me](https://m1.ogoro.me/)

### Contents:

- [Quantum Algorithms](#quantum-algorithms)
- [Web Application](#web-application)
- [AWS Infrastructure](#aws-infrastructure)
- [CloudFormation Stacks](#cloudformation-stacks)

### Quantum Algorithms:

- #### Bernstein-Vazirani:

  Determines hidden message encoded in black-box function.<br>
  Classical algorith complexity is O(N) while quantum is O(1).

  [m1](/app/core-service/core/algorithms/bernvaz.py) |
  [wiki](https://en.wikipedia.org/wiki/Bernstein%E2%80%93Vazirani_algorithm) |
  [qiskit](https://qiskit.org/textbook/ch-algorithms/bernstein-vazirani.html)

- #### Grover:

  Finds elements which satisfy constraints determined by black-box function.<br>
  Classical algorithm complexity is O(N) while quantum is O(square root of N).

  [m1](/app/core-service/core/algorithms/grover.py) |
  [wiki](https://en.wikipedia.org/wiki/Grover%27s_algorithm) |
  [qiskit](https://qiskit.org/textbook/ch-algorithms/grover.html)

- #### Grover Mini Sudoku:

  Finds elements in sudoku-style matrix using Grover quantum search algorithm.<br>
  Classical algorith complexity is O(N) while quantum is O(square root of N).

  [m1](/app/core-service/core/algorithms/grover_sudoku.py) |
  [wiki](https://en.wikipedia.org/wiki/Grover%27s_algorithm) |
  [qiskit](https://qiskit.org/textbook/ch-algorithms/grover.html)

- #### Deutsch-Jozsa:

  Determines if black-box function is constant (returns all 1 or all 0) or balanced (returns half of 1 
  and half of 0).<br>
  Classical algorith complexity is O(2^N) while quantum is O(1).

  [m1](/app/core-service/core/algorithms/dj.py) |
  [wiki](https://en.wikipedia.org/wiki/Deutsch%E2%80%93Jozsa_algorithm) |
  [qiskit](https://qiskit.org/textbook/ch-algorithms/deutsch-jozsa.html)

- #### Simon:

  Finds period of black-box function.<br>
  Classical algorithm complexity is O(2^N) while quantum is O(N^3).

  [m1](/app/core-service/core/algorithms/simon.py) |
  [wiki](https://en.wikipedia.org/wiki/Simon%27s_problem) |
  [qiskit](https://qiskit.org/textbook/ch-algorithms/simon.html)

- #### Quantum Fourier Transform:

  Applies discrete Fourier transform to quantum state amplitudes.<br>
  Classical algorithm complexity is O(N\*2^N) while quantum is O(N*log(N)).

  [m1](/app/core-service/core/algorithms/qft.py) |
  [wiki](https://en.wikipedia.org/wiki/Quantum_Fourier_transform) |
  [qiskit](https://qiskit.org/textbook/ch-algorithms/quantum-fourier-transform.html)

- #### Quantum Phase Estimation:

  Estimates phase for unitary operator.

  [m1](/app/core-service/core/algorithms/qpe.py) |
  [wiki](https://en.wikipedia.org/wiki/Quantum_phase_estimation_algorithm) |
  [qiskit](https://qiskit.org/textbook/ch-algorithms/quantum-phase-estimation.html)
  
- #### Shor:

  Factors integers using quantum spectographer and modular exponentiation.<br>
  Classical algorithm complexity is O(2 ^ square root of N) while quantum is O(N^3).

  [m1](/app/core-service/core/algorithms/shor.py) |
  [wiki](https://en.wikipedia.org/wiki/Shor%27s_algorithm) |
  [qiskit](https://qiskit.org/textbook/ch-algorithms/shor.html)

### Web Application:

- [Flask](https://flask.palletsprojects.com/) framework on [Gunicorn](https://gunicorn.org/) WSGI server
- Quantum computation on real devices with [IBM Qiskit](https://qiskit.org/)
- Telegram bot with [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- Facebook login with [OAuth flow](https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow)
- Frontend with [Bootstrap](https://getbootstrap.com/docs/4.6/getting-started/introduction/)
- 100% [Pytest](https://docs.pytest.org/) [Coverage](https://coverage.readthedocs.io/)
- Multi-process and multi-threaded tasks, queue and execution
- Integration with AWS infrastructure using [Boto3 SDK](https://github.com/boto/boto3#readme)


### AWS Infrastructure:

- Automated infrastructure with [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html)
- Docker containers in [AWS ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html) cluster
- NoSQL DB with [AWS DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)
- API with [AWS API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html) and [Swagger](https://swagger.io/)
- CDN distribution with [AWS CloudFront](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html)
- SSL Certificate from [AWS ACM](https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html) 
- User management with [AWS Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html)
- Virtual IDE in [AWS Cloud9](https://docs.aws.amazon.com/cloud9/latest/user-guide/welcome.html)

### Information:

- 100% of AWS Infrastructure is automatically deployed
- 78 AWS Resources in 8 CloudFormation Stacks
- 150 Unit and Integration tests

### CloudFormation Stacks:

- [Core stack](stack-templates/m1-core-stack.yml):

  VPC, EC2, S3, ELB, AMI, Subnets, Routes, Custom NAT Instances 

- [Cluster stack](stack-templates/m1-cluster-stack.yml):

  ECR, ECS, Fargate, Cluster EC2, ASG, IAM Roles, CloudWatch

- [DNS stack](stack-templates/m1-dns-stack.yml):

  Route 53, ACM Certificate, CloudFront

- [API stack](stack-templates/m1-api-stack.yml):

  REST API, Domain, Deployment, VPC Link

- [CI/CD stack](stack-templates/m1-cicd-stack.yml):

  CodeCommit, CodeBuild, CodePipeline, Artifacts S3, Roles

- [Dynamo stack](stack-templates/m1-dynamo-stack.yml):

  DynamoDB, Tables, GSI, VPC Endpoint

- [Bastion stack](stack-templates/m1-bastion-stack.yml):

  ASG, Launch config

- [Cognito stack](stack-templates/m1-cognito-stack.yml):

  UserPool

### Credits

[M1 Project](#m1-project) 🔥 is being developed by [Mykhailo Ohorodnikov](https://github.com/ogorodnikov) 🌻 in Kyiv, Ukraine 💛💙 under [MIT License](LICENSE)
