# Projeto CI/CD  
## Tecnologias Utilizadas

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Minikube](https://img.shields.io/badge/Minikube-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Github Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Kubernetes](https://img.shields.io/badge/kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![ArgoCD](https://img.shields.io/badge/ArgoCD-EF4836?style=for-the-badge&logo=argo&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![Docker Hub](https://img.shields.io/badge/Docker_Hub-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## Objetivo:
Automatizar o ciclo completo de desenvolvimento, build, deploy e execução de uma aplicação FastAPI simples, usando GitHub Actions para CI/CD, Docker Hub como registry, e ArgoCD para entrega contínua em Kubernetes local com Minikube.

---

### Requisitos:

- Minikube instalado e ativo
- Kubectl configurado (kubectl get nodes funcionando)
- ArgoCD instalado no cluster
- Conta no GitHub com repositórios públicos
- Conta no Docker Hub com token de acesso
- Git instalado
- Python 3 e Docker instalados localmente

---

## Etapa 1 – Criar a aplicação FastAPI
1.	Criar repositório Git para a aplicação (hello-app) com os seguintes arquivos:
- main.py

```
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Olá Mundo!"}
```
---

- requirements.txt

```
fastapi
uvicorn
```
---

- Dockerfile

```
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```
---

2.	Inicializar Git, commit e push para o GitHub:

```
git init
git add .
git commit -m "Aplicação FastAPI inicial"
git branch -M main
git remote add origin https://github.com/<seu_usuario>/hello-app.git
git push -u origin main
```
---

## Etapa 2 – Criar workflow CI/CD no GitHub Actions
1.	Criar estrutura:

```
hello-app/
└── .github/
    └── workflows/
        └── docker-build.yml
```
---

2.	Conteúdo do workflow (docker-build.yml):

```
name: Build and Push Docker Image

on:
  push:
    branches:
      - main

jobs:
  build-and-update-manifests:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: <seu_usuario>/hello-app:latest
```
---

3.	Configurando token de acesso e segredos:

  	Acesse Docker Hub e vamos	criar um Access Token:
-	Vá em Account Settings → Security → Generate new Token
- Nomeie como github-actions-token
- Access permissions: Read, Write, Delete.
- Generate
- Copie o token gerado (será usado como senha)

---

4.	Criando secrets no GitHub:

  	No repositório da aplicação (hello-app):
-	Vá em Settings → Secrets and Variables → Actions → New repository secret
- Crie os seguintes secrets:

    DOCKER_USERNAME: Seu nome de usuário do Docker Hub.

    DOCKER_PASSWORD: Token de acesso do Docker Hub, criado na etapa 3.1.

    SSH_PRIVATE_KEY: Opcional caso queira acessar via SSH, se sim, coloque a chave privada.

---

5.  Commit e push do workflow:

```
git add .github/workflows/docker-build.yml
git commit -m "Adiciona workflow de build e push do Docker"
git push origin main
```

Com isso a imaagem foi criada no docker hub.

![WhatsApp Image 2025-11-09 at 15 46 11](https://github.com/user-attachments/assets/007df66f-b402-468e-84da-9ad275675acc)

---

## Etapa 3 – Criar repositório de manifests para ArgoCD
- Criar repositório GitHub (hello-manifests).
- Estrutura dos arquivos:

```
hello-manifests/
├── deployment.yaml
└── service.yaml
```
---

- deployment.yaml

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hello-app
  template:
    metadata:
      labels:
        app: hello-app
    spec:
      containers:
      - name: hello-app
        image: gabrielchialle/hello-app:latest
        ports:
        - containerPort: 80
```
---

- service.yaml

```
apiVersion: v1
kind: Service
metadata:
  name: hello-app
spec:
  selector:
    app: hello-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
```

Commit e push para o repositório de manifests.
---

## Etapa 4 – Criar app no ArgoCD
1.	Conectar ArgoCD ao repositório de manifests:

```
argocd repo add https://github.com/<seu_usuario>/hello-manifests.git \
  --username <github-username> \
  --password <personal-access-token>
```
---

2.  Criar aplicação no ArgoCD apontando para o repositório e namespace:
```
argocd app create hello-app \
  --repo https://github.com/<seu_usuario>/hello-manifests.git \
  --path . \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace hello-app
```
---

3.  Sincronizar a aplicação:
```
argocd app sync hello-app
```
---

4.  Acessar ArgoCD via port-forward:
```
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

 Abrir no navegador [http://localhost:8080](http://localhost:8080)
 - Usuário: admin
 - Para obter a senha rode:
```
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```

![WhatsApp Image 2025-11-09 at 15 46 11(1)](https://github.com/user-attachments/assets/94c57be5-3b99-4092-907c-3de2f4282d48)

---

## Etapa 5 – Acessar e testar a aplicação
1.	Criar namespace e aplicar manifests:

```
kubectl create namespace hello-app
kubectl apply -n hello-app -f deployment.yaml
kubectl apply -n hello-app -f service.yaml
```
---

2.  Verificar pods:

```
kubectl get pods -n hello-app
kubectl get svc -n hello-app
```

<img width="1366" height="768" alt="Captura de tela de 2025-11-09 18-01-39" src="https://github.com/user-attachments/assets/cc4cf189-fcc5-406e-86d0-5230fa5a8af6" />

---

3.  Acessar aplicação via port-forward:

```
kubectl port-forward svc/hello-app -n hello-app 9090:80
```
Abrir no navegador [http://localhost:9090](http://localhost:9090)

![WhatsApp Image 2025-11-09 at 15 46 12(2)](https://github.com/user-attachments/assets/d2b221ae-555a-47b1-83ad-0c5e146c003d)

---

## Verificação

Mude o seu script em main.py, dê commit e push para ver se atualiza a aplicação. Atualizando, acesse novamente seu local host e seu projeto estará completo!!!

![WhatsApp Image 2025-11-09 at 15 46 12(1)](https://github.com/user-attachments/assets/42df2a49-fdf4-4dd3-83b7-643ad1796f20)
