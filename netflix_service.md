# Netflix Service 

1. Repos link

- https://github.com/exit-zero-academy/NetflixFrontend
- https://github.com/exit-zero-academy/NetflixMovieCatalog

2. Build docker images and run them locally.
3. Push your images to DockerHub.
4. Create a new GitHub repo called `NetflixInfra`.
5. Deploy the Netflix stack in a Kubernetes cluster. Create a `Deployment` and `Service` for each microservice. Put your YAML manifests in `NetflixInfra`.  
   Make sure the service is up and running by `port-forward`ing your NetflixFrontend service locally. 
6. Install ArgoCD: https://argo-cd.readthedocs.io/en/stable/getting_started/
   read the ArgoCD initial secret by: `kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath='{.data.*}' | base64 -d`.
7. Define the `netflix-frontend` and `netflix-catalog` apps in ArgiCD and check the CD automation by committing and pushing changes in your YAML manifests. 
8. Run a Jenkins server locally by:

```bash
cd jenkins_docker
docker compose up
```

9. Configure Jenkins agent as follows: 


   1. In you Jenkins main Dashboard, go to **Manage Jenkins** > **Nodes** > **New Node**.
   2. Give your node a name: `agent1`, and choose the **Permanent Agent**.
   3. In **Number of executors** choose **1**. This defines the number of concurrent pipelines that can run on the agent. Usually should be set to the number of cores on the machine the agents runs on. 
   4. Under **Remote root directory** specify `/home/jenkins/agent` (the directory on the agent where Jenkins will store files).
   5. Assign a label to the agent, e.g. `general`. The label will be later used to assign pipelines specifically on an agent having this label.
   6. Keep all other default configurations and choose **Save**.
   7. On the **Nodes** page, find your newly created agent and click on it. You'll see the join secret the Jenkins agents has to have in order to authenticate in the Jenkins controller.
   8. Modify the `.env` file accordingly.

10. Create in Jenkins credentials called `dockerhub` with your DockerHub credentials. 
9. Create a Build pipeline based on: 

```text
pipeline {
    agent {
        label 'general'
    }
    
    triggers {
        githubPush()   // trigger the pipeline upon push event in github
    }
    
    environment {        
        IMAGE_TAG = "v1.0.$BUILD_NUMBER"
        IMAGE_BASE_NAME = "netflix-frontend"
        
        DOCKER_CREDS = credentials('dockerhub')
        DOCKER_USERNAME = "${DOCKER_CREDS_USR}"  // The _USR suffix added to access the username value 
        DOCKER_PASS = "${DOCKER_CREDS_PSW}"      // The _PSW suffix added to access the password value
    } 

    stages {
        stage('Docker setup') {
            steps {             
                sh '''
                  docker login -u $DOCKER_USERNAME -p $DOCKER_PASS
                '''
            }
        }
        
        stage('Build & Push') {
            steps {             
                sh '''
                  IMAGE_FULL_NAME=$DOCKER_USERNAME/$IMAGE_BASE_NAME:$IMAGE_TAG
                
                  docker build ...
                  docker push ...
                '''
            }
        }
    }
}
```


In the **NetflixInfra** repo (the dedicated repo you've created for the Kubernetes YAML manifests for the Netflix stack), create another `Jenkinsfile` under `pipelines/deploy.Jenkinsfile`, as follows:

```text
pipeline {
    agent any
    
    parameters { 
        string(name: 'SERVICE_NAME', defaultValue: '', description: '')
        string(name: 'IMAGE_FULL_NAME_PARAM', defaultValue: '', description: '')
    }

    stages {
        stage('Deploy') {
            steps {
                /*
                
                Now your turn! implement the pipeline steps ...
                
                - `cd` into the directory corresponding to the SERVICE_NAME variable. 
                - Change the YAML manifests according to the new $IMAGE_FULL_NAME_PARAM parameter.
                  You can do so using `yq` or `sed` command, by a simple Python script, or any other method.
                - Commit the changes, push them to GitHub. 
                   * Setting global Git user.name and user.email in 'Manage Jenkins > System' is recommended.
                   * Setting Shell executable to `/bin/bash` in 'Manage Jenkins > System' is recommended.
                */ 
            }
        }
    }
    post {
        cleanup {
            cleanWs()
        }
    }
}
``` 

Carefully review the pipeline and complete the step yourself. 

In the Jenkins dashboard, create another Jenkins **Pipeline** (e.g. named `NetflixFrontendDeploy`). Configure it similarly to the Build pipeline - choose **Pipeline script from SCM**, and specify the Git URL, branch, path to the Jenkinsfile, **as well as your created GitHub credentials** (as this pipeline has to push commit on your behalf).  

As can be seen, unlike the Build pipeline, the Deploy pipeline is not triggered automatically upon a push event in GitHub (there is no `githubPush()`...)
but is instead initiated by providing a parameter called `IMAGE_FULL_NAME_PARAM`, which represents the new Docker image to deploy to your Kubernetes cluster. 

Now to complete the Build-Deploy flow, configure the Build pipeline to trigger the Deploy pipeline and provide it with the `IMAGE_FULL_NAME_PARAM` parameter by adding the following stage after a successful Docker image build: 

```diff
stages {

  ...

+ stage('Trigger Deploy') {
+     steps {
+         build job: '<deploy-pipeline-name-here>', wait: false, parameters: [
+             string(name: 'SERVICE_NAME', value: "NetflixFrontend"),
+             string(name: 'IMAGE_FULL_NAME_PARAM', value: "$IMAGE_FULL_NAME")
+         ]
+     }
+ }

}
```

Where `<deploy-pipeline-name-here>` is the name of your Deploy pipeline (should be `NetflixFrontendDeploy` if you followed our example).

Test your simple CI/CD pipeline end-to-end.

## Expose the Jenkins server publicly

3. Expose the Jenkins server using Ngrok static domain:
   1. If haven't done yet, create your [Ngrok account](https://ngrok.com/), download and install the tool. 
   1. In the main menu of your account page, click **Setup and installation**. Under **Deploy your app online**, enable a **static domain**. 
   1. Expose your Jenkins server by `ngrok http --domain=<my-static-domain> 8080` (change `<my-static-domain>` accordingly). 
4. Open up your browser and visit the Jenkins server by `https://<my-static-domain>`. 


## Configure a GitHub webhook

Create credentials in Jenkins to allow you to authenticate with GitHub for accessing repositories and managing webhooks.

1. **Kind** must be **Username and password**.
2. Choose informative **Username** (as **github** or something similar)
3. The **Password** should be a GitHub Personal Access Token with the following scope:
   ```text
   repo,read:user,user:email,write:repo_hook
   ```
   Click [here](https://github.com/settings/tokens/new?scopes=repo,read:user,user:email,write:repo_hook) to create a token with this scope.
4. Enter `github` as the credentials **ID**.


A **GitHub webhook** is a mechanism that allows GitHub to notify a Jenkins server when changes occur in the repo. 
When a webhook is configured, GitHub will send a HTTP POST request to a specified URL whenever a specified event, such as a push to the repository, occurs.

1. If you don't have it yet, **fork** both the [NetflixFrontend][NetflixFrontend] and the [NetflixMovieCatalog][NetflixMovieCatalog] repos. 
2. On **each** GitHub repository page, go to **Settings**. From there, click **Webhooks**, then **Add webhook**.
3. In the **Payload URL** field, type `https://<your-jenkins-ngrok-url>/github-webhook/`. In the **Content type** select: `application/json` and leave the **Secret** field empty.
4. Choose the following events to be sent in the webhook:
    1. Pushes
    2. Pull requests

## The Build and Deploy phases - overview

![][jenkins_build_deploy]


# The Netflix Service: Full CI/CD workflow

You'll design and implement a full CI/CD pipeline for the Netflix stack both Development and Production environments
using Jenkins.

## Guidelines

- Create the following pipelines in Jenkins:
  - In the **NetflixFrontend** repo under `pipelines/` dir:
    - `build-prod.Jenkinsfile` - triggered upon changes on `main` branch.
    - `build-dev.Jenkinsfile` - triggered upon changes on `dev` branch.
    - `test.Jenkinsfile` - triggered upon changes in Pull Request branches (no need to implement real testing).
  - In the **NetflixMovieCatalog** repo under `pipelines/` dir:
    - `build-prod.Jenkinsfile` - triggered upon changes on `main` branch.
    - `build-dev.Jenkinsfile` - triggered upon changes on `dev` branch.
    - `test.Jenkinsfile` - triggered upon changes in Pull Request branches.
  - In the **NetflixInfra** repo:
    - `netflix-deploy-prod.Jenkinsfile` - triggered by the build prod pipelines, pushes changes to branch `main`.
    - `netflix-deploy-dev.Jenkinsfile` - triggered by the build dev pipelines, pushes changes to branch `dev`.

### The workflow


You want to develop a new feature in the **NetflixMovieCatalog** microservice. 
Here is the workflow that should be used:

1. In the **NetflixMovieCatalog** repo, from an updated branch `main` (pull it if needed), create a new branch called `feature/new_feature`.
2. Commit your code changes.
3. To test your change in development env, checkout branch `dev` and merge your feature branch **into** `dev`.
4. Push to GitHub, let the `build-dev` pipeline to build a new version, push it to DockerHub, and trigger the `netflix-deploy-dev` pipeline.
5. Make sure the feature is reflected in your k8s cluster for dev app. 
6. If there are some fixes to do, checkout `feature/new_feature` again, commit your fixes. Merge then into `dev` branch and push it. 
7. Once you are satisfied with the results, it's time to deploy to production. 
8. Push branch `feature/new_feature` to GitHub and create a Pull Request from `feature/new_feature` branch into `main` branch of your repo. 
9. Review the PR (in real world, this is the step where an extensive testing is performed), let Jenkins execute the `test` pipeline, and approve it. 
10. Once the `feature/new_feature` was merge into `main`, the `build-prod` pipeline would be triggered and then the `netflix-deploy-prod` in turn, deploying the changes into prod app in the k8s cluster.

As can be seen, when setting an automated deployment pipeline on branch `main`, a developer can by mistake commit and push some change from his local machine directly on branch `main`, and that in turn will trigger an automated deployment pipeline. 
Thus, to protect branch `main`, you should [configure a protection rule](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule#creating-a-branch-protection-rule) on branch `main` that enforces a PR review before merging.

**Work properly! Don't be tempted to commit and push directly on `dev` and `main` branches.** 
The only branch to commit changes is your feature branch. 
When you want to test it on dev env, merge your feature branch into `dev` and push. When you want to have it in prod, create a PR from your feature branch into `main`, review and merge. 


![][git_envbased]

[git_envbased]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_envbased.png


[jenkins_build_deploy]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/jenkins_build_deploy.png



