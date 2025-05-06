# OpenLLM Gateway

[![dev-deployment-frontend](https://github.com/timkrebs9/openllm-gateway/actions/workflows/dev-deployment-frontend.yml/badge.svg)](https://github.com/timkrebs9/openllm-gateway/actions/workflows/dev-deployment-frontend.yml)
[![dev-deployment-chat](https://github.com/timkrebs9/openllm-gateway/actions/workflows/dev-deployment-chat.yml/badge.svg)](https://github.com/timkrebs9/openllm-gateway/actions/workflows/dev-deployment-chat.yml)
[![dev-deployment-auth](https://github.com/timkrebs9/openllm-gateway/actions/workflows/dev-deployment-auth.yml/badge.svg)](https://github.com/timkrebs9/openllm-gateway/actions/workflows/dev-deployment-auth.yml)

OpenLLM Gateway is a modular, cloud-native platform for deploying and managing LLM-based chat and authentication services on Azure Kubernetes Service (AKS). It leverages best practices for Azure, GitHub Actions CI/CD, and infrastructure-as-code with Terraform.

---

## Features

- **Frontend Service**: Flask-based web UI for users.
- **Chat Service**: FastAPI backend for LLM chat, connects to Ollama and Auth services.
- **Auth Service**: FastAPI-based authentication with PostgreSQL backend.
- **Ollama Service**: LLM inference via Ollama.
- **Kubernetes Manifests**: For all services, ready for AKS.
- **Terraform Infrastructure**: Automated provisioning of Azure resources (AKS, ACR, DNS, Key Vault, Application Insights, Log Analytics, etc.).
- **CI/CD**: GitHub Actions for build, push, and deploy to AKS.
- **Azure Best Practices**: Secure, scalable, and observable by default.

---

## Project Structure

```
openllm-gateway/
├── infra/                  # Terraform IaC for Azure resources
├── scripts/                # Utility scripts (e.g., DB init)
└── src/
    ├── auth-service/       # FastAPI Auth microservice
    ├── chat-service/       # FastAPI Chat microservice
    ├── frontend-service/   # Flask frontend
    ├── ollama-service/     # Ollama LLM deployment
    ├── ingress/            # Ingress manifests
    └── cert-manager/       # Cert-manager manifests
```

---

## Getting Started

### Prerequisites

- Azure Subscription
- [Terraform](https://learn.hashicorp.com/terraform)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- Docker
- Python 3.11+ (for local dev)

### 1. Provision Azure Infrastructure

```sh
cd infra
terraform init
terraform apply
```

This will provision AKS, ACR, DNS, Key Vault, Application Insights, and more.

### 2. Build and Push Docker Images

Each service has a Dockerfile. Example for auth-service:

```sh
cd src/auth-service
docker build -t <acr-name>.azurecr.io/auth-service:latest .
az acr login --name <acr-name>
docker push <acr-name>.azurecr.io/auth-service:latest
```

Or use the provided GitHub Actions workflows for automated CI/CD.

### 3. Deploy to AKS

Apply Kubernetes manifests:

```sh
kubectl apply -f src/auth-service/manifests/
kubectl apply -f src/chat-service/manifests/
kubectl apply -f src/frontend-service/manifests/
kubectl apply -f src/ollama-service/manifests/
kubectl apply -f src/ingress/
```

### 4. Access the Application

- The frontend will be available at the DNS configured in your ingress (e.g., `https://chat.azureopengpt.com`).
- Auth and chat endpoints are exposed via ingress and secured with OAuth2.

---

## Local Development

- Each service can be run locally with Docker Compose or individually.
- Use `.env` files for local environment variables.
- See each service's `requirements.txt` for dependencies.

---

## Security & Best Practices

- Secrets are managed via Azure Key Vault.
- TLS is managed via cert-manager and Azure Key Vault integration.
- Application Insights and Log Analytics are enabled for observability.
- Follows Azure naming, tagging, and RBAC best practices.

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](https://opensource.microsoft.com/codeofconduct/).

---

## License

This project is licensed under the [MIT License](LICENSE.md).

---

## Acknowledgements

- [Ollama](https://ollama.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Flask](https://flask.palletsprojects.com/)
- [Azure](https://azure.microsoft.com/)
- [Terraform](https://www.terraform.io/)
