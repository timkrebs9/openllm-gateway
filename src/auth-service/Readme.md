1. Lokales Testen:
   ```bash
   docker build -t auth-service .
   docker run -p 8000:8000 --env-file .env auth-service
   ```

2. Push zu DockerHub:
   ```bash
   docker tag auth-service your-dockerhub-username/auth-service:latest
   docker push your-dockerhub-username/auth-service:latest
   ```

3. Deployment nach Kubernetes:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```
