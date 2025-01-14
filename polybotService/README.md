# The Polybot Service: AWS Project

## Preliminaries



1. Create a dedicated GitHub repo.
2. Copy the content of `polybotService/` into the new repo:

```text
/ (root)
│
├── polybot/
│   ├── ...
│
└── yolo5/
    ├── ...
```

### Create a Telegram Bot

1. <a href="https://desktop.telegram.org/" target="_blank">Download</a> and install Telegram Desktop (you can use your phone app as well).
2. Once installed, create your own Telegram Bot by following <a href="https://core.telegram.org/bots/features#botfather">this section</a> to create a bot. Once you have your telegram token you can move to the next step.

**Never** commit your telegram token in Git repo, even if the repo is private.
For now, we will provide the token as an environment variable to your chat app. 
Later on in the course we will learn better approaches to store sensitive data.

### Running the Telegram bot locally

The Telegram app is a flask-based service that responsible for providing a chat-based interface for users to interact with your image processing functionality. 
It utilizes the Telegram Bot API to receive user images and respond with processed images. 

The code skeleton for the bot app is already given to you under `polybot/app.py`.
In order to run the server, you have to [provide 2 environment variables](https://www.jetbrains.com/help/objc/add-environment-variables-and-program-arguments.html#add-environment-variables):

1. `TELEGRAM_TOKEN` which is your bot token.
2. `TELEGRAM_APP_URL` which is your app public URL provided by Ngrok (will be discussed soon).

Implementing bot logic involves running a local Python script that listens for updates from Telegram servers.
When a user sends a message to the bot, Telegram servers forward the message to the Python app using a method called **webhook** (**long-polling** and **websocket** are other possible methods which wouldn't be used in this project).
The Python app processes the message, executes the desired logic, and may send a response back to Telegram servers, which then delivers the response to the user.

The webhook method consists of simple two steps:

Setting your chat app URL in Telegram Servers:

![][python_project_webhook1]

Once the webhook URL is set, Telegram servers start sending HTTPS POST requests to the specified webhook URL whenever there are updates, such as new messages or events, for the bot. 

![][python_project_webhook2]


You've probably noticed that setting `localhost` URL as the webhook for a Telegram bot can be problematic because Telegram servers need to access the webhook URL over the internet to send updates.
As `localhost` is not accessible externally, Telegram servers won't be able to reach the webhook, and the bot won't receive any updates.

[Ngrok](https://ngrok.com/) can solve this problem by creating a secure tunnel between the local machine (where the bot is running) and a public URL provided by Ngrok.
It exposes the local server to the internet, allowing Telegram servers to reach the webhook URL and send updates to the bot.

Sign-up for the Ngrok service (or any another tunneling service to your choice), then install the `ngrok` agent as [described here](https://ngrok.com/docs/getting-started/#step-2-install-the-ngrok-agent). 

Authenticate your ngrok agent. You only have to do this once:

```bash
ngrok config add-authtoken <your-authtoken>
```

Since the telegram bot service will be listening on port `8443`, start ngrok by running the following command:

```bash
ngrok http 8443
```

Your bot public URL is the URL specified in the `Forwarding` line (e.g. `https://16ae-2a06-c701-4501-3a00-ecce-30e9-3e61-3069.ngrok-free.app`).
Don't forget to set the `TELEGRAM_APP_URL` env var to your URL. 

In the next step you'll finally run your bot app.

## Infrastructure

- If you don't have it yet, create a VPC with at least two public subnets in different AZs.
- During the project you'll deploy the Polybot Service in EC2 instances. For that, your instances has to have permission on some AWS services (E.g. for example to upload/download photos in S3).
  The correct way to do it is by attaching an **IAM role** with the required permissions to your EC2 instance. **Don't** use or generate access keys.

> [!WARNING]
> Never commit AWS credentials into your git repo nor your Docker containers!

## Provision the `polybot` microservice

![][botaws2]

- The Polybot microservice should be running in a `micro` EC2 instance. You'll find the code skeleton under `polybot/`. Take a look at it - it's similar to the one used in the previous project, so you can leverage your code implementation from before.
- The app should be running automatically as the EC2 instances are being started (in case the instance was stopped), **without any manual steps**.      
  
  There are many approached to achieve that, for example by using the `--restart always` flag in the `docker run` command, or using a Linux service.
- The service should be highly available. For that, you'll use an **Application Load Balancer (ALB)** that routes the traffic across the instances located in different AZs. 
  
  The ALB must have an **HTTPS** listener, as working with **HTTP** [is not allowed](https://core.telegram.org/bots/webhooks) by Telegram. To use HTTPS you need a TLS certificate. You can get it either by:
  - [Generate a self-signed certificate](https://core.telegram.org/bots/webhooks#a-self-signed-certificate) and import it to the ALB listener. In that case the certificate `Common Name` (`CN`) must be your ALB domain name (E.g. `test-1369101568.eu-central-1.elb.amazonaws.com`), and you must pass the certificate file when setting the webhook in `bot.py` (i.e. `self.telegram_bot_client.set_webhook(..., certificate=open(CERTIFICATE_FILE_NAME, 'r'))`).
  
    Or 

  - [Register a real domain using Route53](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/domain-register.html) (`.click` is one of the cheapest). After registering your domain, in the domain's **Hosted Zone** you should create a subdomain **A alias record** that routes traffic to your ALB. In addition, you need to request a **public certificate** for your domain address, since the domain has been issued by Amazon, issuing a certificate [can be easily done with AWS Certificate Manager (ACM)](https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request-public.html#request-public-console). 

- [Read Telegram's webhook docs](https://core.telegram.org/bots/webhooks) to get the CIDR of Telegram servers. Since your ALB is publicly accessible, it's better to restrict incoming traffic access to the ALB exclusively to Telegram servers by applying inbound rules to the **Security Group**.
- Your Telegram token is a sensitive data. It should be stored in [AWS Secret Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html). Create a corresponding secret in Secret Manager, under **Secret type** choose **Other type of secret**.

## Provision the `yolo5` microservice

![][botaws3]

- The Yolo5 microservice should be running within a `medium` EC2 instance. The service files can be found under `yolo5/`. In `app.py` you'll find a code skeleton that periodically consumes jobs from an **SQS queue**. 
- **Polybot -> Yolo5 communication:** When the Polybot microservice receives a message from Telegram servers, it uploads the image to the S3 bucket. 
    Then, instead of talking directly with the Yolo5 microservice using a simple HTTP request, the bot sends a "job" to an SQS queue.
    The job message contains information regarding the image to be processed, as well as the Telegram `chat_id`.
    The Yolo5 microservice acts as a consumer, consumes the jobs from the queue, downloads the image from S3, processes the image, and writes the results to a **DynamoDB table** (instead of MongoDB as done in the previous Docker project. Change your code accordingly).
- **Yolo5 -> Polybot communication:** After writing the results to DynamoDB, the Yolo5 microservice then sends a `POST` HTTP request to the Yolo5 microservice, to `/results?predictionId=<predictionId>`, while `<predictionId>` is the prediction ID of the job the yolo5 worker has just completed. 
  The request is done via the ALB domain address (you can use the existed HTTPS listener or create an HTTP listener).
  The `/results` endpoint in the Polybot microservice then should retrieve the results from DynamoDB and sends them to the end-user Telegram chat by utilizing the `chat_id` value.
- The Yolo5 microservice should be **auto-scaled**. For that, all Yolo5 instances would be part of an **Auto-scaling Group**. 
  Create a Launch Template and Autoscaling Group with **desired capacity 1**, and **maximum capacity of 2** (obviously in real-life application it would be more than 2).
  The automatic scaling based on **CPU utilization**, with a scaling policy triggered when the CPU utilization reaches **60%**.
- The Yolo5 app should be automatically up and running when an instance is being started as part of the ASG, without any manual steps. 
  You can utilize [User Data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html) to achieve that. 

## Test your service scalability

1. Send multiple images to your Telegram bot within a short timeframe to simulate increased traffic.
2. Navigate to the **CloudWatch** console, observe the metrics related to CPU utilization for your Yolo5 instances. You should see a noticeable increase in CPU utilization during the period of increased load.
3. After ~3 minutes, as the CPU utilization crosses the threshold of 60%, **CloudWatch alarms** will be triggered.
   Check your ASG size, you should see that the desired capacity increases in response to the increased load.
4. After approximately 15 minutes of reduced load, CloudWatch alarms for scale-in will be triggered.

## Integrate a simple CI/CD pipeline

We now want to automate the deployment process of the service, both for the Polybot and the Yolo5 microservices.  
Meaning, when you make code changes locally, then commit and push them, a new version of Docker image is being built and deployed into the designated EC2 instances (either the two instances of the Polybot or all ASG instances of the Yolo5).
The process has to be **fully automated**. 

While the expected outcome is simple, there are many ways to implement it.
You are given a skeleton for GitHub Action workflows for the Polybot and the Yolo5 under `.github/workflows/polybot-deployment.yaml` and `.github/workflows/yolo5-deployment.yaml` respectively.

Beyond the provided YAMLs, you are free to design and implement your CI/CD pipeline in any way you see, here are some ideas:

- To build your images:
  - Simply by `docker` commands in the GitHub Actions workflow.
  - Use [AWS CodeBuild](https://docs.aws.amazon.com/codebuild/latest/userguide/getting-started-overview.html).

- To deploy a new image version:
  - Simply by a bash script that lists EC2 instances according to some tag and execute commands within each instance to pull and run the new image version.
  - Use Ansible playbook.
  - [AWS CodeDeploy](https://docs.aws.amazon.com/codedeploy/latest/userguide/welcome.html).
  - [ASG instance refresh](https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html).

Test your CI/CD pipline for both the Polybot and Yolo5 microservices.


# Good Luck

[DevOpsTheHardWay]: https://github.com/exit-zero-academy/DevOpsTheHardWay
[onboarding_tutorial]: https://github.com/exit-zero-academy/DevOpsTheHardWay/blob/main/tutorials/onboarding.md
[github_actions]: ../../actions

[PolybotServiceDocker]: https://github.com/exit-zero-academy/PolybotServiceDocker
[botaws2]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/aws_project_botaws2.png
[botaws3]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/aws_project_botaws3.png
[python_project_webhook1]: https://alonitac.github.io/DevOpsTheHardWay/img/python_project_webhook1.png
[python_project_webhook2]: https://alonitac.github.io/DevOpsTheHardWay/img/python_project_webhook2.png