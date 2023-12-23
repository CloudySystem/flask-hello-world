# KubeOps Challenge

This repository contains a simple dockerized Flask application (`app.py`), GitHub Action workflow (`.github/workflows/deploy.yaml`), the K8s Deployment and Service YAML files (`manifests/`) and the ArgoCD configuration files (`argocd/`).

## 1. Deploy `minikube` cluster
```shell
# Install minikube binary
brew install minikube

# Start minikube
minikube start
```

## 2. Initial Container Deployment

A simple Flask server will be used as Hello World app. It launches an HTTP server at port 5000 and returns some welcoming HTML when hit at `GET /` endpoint.

### Manually Build and Push FlaskHelloWorld Docker Image
```shell
# Build Docker Image
docker build -t docker.io/cloudysystem/flask-hello-world:latest .

# Test local run
docker run -p 5000:5000 docker.io/cloudysystem/flask-hello-world

# Open browser or use curl to validate it works
curl localhost:5000

# Login to DockerHub
docker login docker.io

# Push to DockerHub
docker push docker.io/cloudysystem/flask-hello-world:latest
```

### Deploy using manifests 

A simple and quick way to deploy the app once built.

```shell
# Pull custom `flask-hello-world` Docker image in minikube
minikube image pull docker.io/cloudysystem/flask-hello-world

# Verify image named `docker.io/cloudysystem/flask-hello-world` is present in minikube
minikube image ls --format=table

# Install `flask-hello-world` using manifests (deployment + service)
minikube kubectl -- apply -f ./manifests
```

## 3. Automate with Action Workflow

A GitHub Action workflow, found at `.github/workflows/publish.yaml` folder, automates the multiarchitecture containerization of the app into Docker images and publishing to DockerHub image registry with appropriate tag depending on the enviroment we intend to deploy to:

### Common Steps

Trigger: When a new commit is pushed to `main` or a new tag using semver notation is pushed

1. Checkout Code Repository
2. Login to DockerHub (_Requires `DOCKER_USERNAME` & `DOCKER_PASSWORD` configured as GitHub Action secrets_).
3. Configure QEMU for multiarch images
4. Configure Docker Buildx for multiarch images

### Staging Deployment

Trigger: When a new commit is pushed to `main` branch

- Build & Push Docker Image tagged with `commitHash` to DockerHub registry
- Update & Push Staging `{Chart,values}.yaml` to match newly pushed commit hash (_Requires Workflow Write Permission over the repository_)

### Production Deployment

Trigger: When a new tag using semver notation (i.e. `v1.2.3`) is pushed.

- Extract Docker Metadata
- Build & Push Docker Image tagged with `v1.2.3` to DockerHub
- Update & Push Production `{Chart,values}.yaml` to match newly pushed tag (_Requires Workflow Write Permission over the repository_)


## 4. ArgoCD Configuration

Now there is all these Docker images published with their respective version tag (semver convention intended for Production deployment and commitHash for Staging deployment) and some Helm Chart value files referencing these updated versions.

To automate the syncronization between the repo, the different environments and the cluster; we can create two ArgoCD Applications: `production-app` and `staging-app`. Each of which references the appropriate path in the repository (i.e `argocd/production`) which contains environment-specific variables. Also, the `argocd.argoproj.io/manifest-generate-paths` label allows the environment-specific Application to only reconcile when the files under that specified repository path are changed; isolating deployment flows across environments.

```shell
# Create ArgoCD Namespace
minikube kubectl -- create ns argocd

# Add ArgoCD Helm Repository
helm repo add argo https://argoproj.github.io/argo-helm

# Create an ArgoCD helm release named `argocd`
helm install -n argocd argocd argo/argo-cd

# Install ArgoCD project and applications
minikube kubectl -- apply -f ./argocd
```

Once the ArgoCD project and applications are created, they will be visible on the ArgoCD Web UI.
```shell
# Port Forward ArgoCD Web UI locally to port 8080
minikube kubectl --  -n argocd port-forward svc/argocd-server 8080:443

# Get secret initial admin password
minikube kubectl -- -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Launch browser and visit ArgoCD Web UI on https://localhost:8080 
# User: admin
# Password: Extracted from previous command
```

## Clean Up
```shell
# Delete ArgoCD project and applications
minikube kubectl -- delete -f ./argocd

# Delete ArgoCD objects
helm uninstall -n argocd argocd

# Delete ArgoCD namespace
minikube kubectl -- delete namespace argocd

# Uninstall `hello-world` chart release
minikube kubectl -- delete -f ./manifests

# Stop minikube
minikube stop
```
