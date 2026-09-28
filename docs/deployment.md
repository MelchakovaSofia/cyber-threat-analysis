# Розгортання в Microsoft Azure

## 1. Ресурси

```bash
# Set your environment variables
export RESOURCE_GROUP="cta-rg"
export LOCATION="westeurope"
export ACR_NAME="ctaacr"  # Replace with your unique ACR name
export AKS_NAME="cta-aks"
export POSTGRES_NAME="cta-postgres"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# Create PostgreSQL database
az postgres flexible-server create --resource-group $RESOURCE_GROUP --name $POSTGRES_NAME \
  --admin-user cta --admin-password '<strong-password>' --tier Burstable --sku-name Standard_B1ms

# Create AKS cluster and attach ACR
az aks create --resource-group $RESOURCE_GROUP --name $AKS_NAME --node-count 2 --attach-acr $ACR_NAME
```

## 2. Налаштування секретів

Перед розгортанням необхідно налаштувати Kubernetes секрети:

```bash
# Generate a strong secret key
export SECRET_KEY=$(openssl rand -base64 32)
export DB_PASSWORD='<your-postgres-password>'

# Create secrets using the provided script
cd kubernetes
chmod +x setup-secrets.sh
DB_PASSWORD=$DB_PASSWORD SECRET_KEY=$SECRET_KEY ./setup-secrets.sh
```

Або створіть секрет вручну:

```bash
kubectl create secret generic cta-secret \
  --from-literal=DATABASE_URL="postgresql+psycopg2://cta:$DB_PASSWORD@cta-postgres:5432/cta_db" \
  --from-literal=SECRET_KEY="$SECRET_KEY"
```

## 3. Образ

```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build and push Docker image
export ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer --output tsv)
docker build -f docker/Dockerfile -t $ACR_LOGIN_SERVER/cta-backend:latest .
docker push $ACR_LOGIN_SERVER/cta-backend:latest

# Update deployment.yaml with your ACR name
sed -i "s/your-acr-name/$ACR_NAME/" kubernetes/deployment.yaml
```

## 4. Kubernetes

```bash
# Get AKS credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME

# Apply Kubernetes manifests
kubectl apply -f kubernetes/pvc.yaml
kubectl apply -f kubernetes/configmap.yaml
# Skip secret.yaml if you already created it manually
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml

# Update ingress host and apply
sed -i "s/cta.example.com/your-domain.com/" kubernetes/ingress.yaml
kubectl apply -f kubernetes/ingress.yaml
```

## 5. Перевірка розгортання

```bash
# Check pod status
kubectl get pods -l app=cta-backend

# Check services
kubectl get services

# Check ingress
kubectl get ingress

# View logs
kubectl logs -l app=cta-backend --tail=50
```

## 6. Моніторинг

Azure Monitor / Container Insights вмикається для кластера AKS;
ендпоїнт `/health` використовується як readiness та liveness probe.
