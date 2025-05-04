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

