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


## The Build and Deploy phases - overview

![][jenkins_build_deploy]


[jenkins_build_deploy]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/jenkins_build_deploy.png



