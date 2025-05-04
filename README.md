[![dev-deployment-frontend](https://github.com/timkrebs9/openllm-gateway/actions/workflows/dev-deployment-frontend.yml/badge.svg)](https://github.com/timkrebs9/openllm-gateway/actions/workflows/dev-deployment-frontend.yml)

[![dev-deployment-chat](https://github.com/timkrebs9/openllm-gateway/actions/workflows/dev-deployment-chat.yml/badge.svg)](https://github.com/timkrebs9/openllm-gateway/actions/workflows/dev-deployment-chat.yml)

[![dev-deployment-auth](https://github.com/timkrebs9/openllm-gateway/actions/workflows/dev-deployment-auth.yml/badge.svg)](https://github.com/timkrebs9/openllm-gateway/actions/workflows/dev-deployment-auth.yml)

Projectstruktur:
openll-gateway:
├── infra/
└──src/
    ├── auth-service/
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── server.py
    │   │   ├── router.py
    │   │   ├── models.py
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── manifests/
    │       ├── deployment.yaml
    │       └── service.yaml
    │
    ├── cert-manager/
    │   └── cluster-ingress.yaml 
    │   
    ├── chat-service/
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── server.py
    │   │   ├── router.py
    │   │   ├── models.py
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── manifests/
    │       ├── deployment.yaml
    │       └── service.yaml
    │
    ├── ollama-services/
    │   └── manifests/
    │       ├── deployment.yaml
    │       └── service.yaml
    │
    ├── ingress/
    │   └── ingress.yaml 
    │
    └── frontend-service/

