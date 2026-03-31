# Parte 3 – Kubernetes

## Visão Geral

Os manifestos Kubernetes estão organizados em `k8s/app/` e cobrem os recursos necessários para executar a aplicação em um cluster.

```
k8s/
└── app/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    └── secret.yaml
```

---

## Pré-requisitos

- Cluster Kubernetes rodando (ex: Kind, Minikube, EKS)
- `kubectl` configurado apontando para o cluster
- Namespace `app` criado:

```bash
kubectl create namespace app
```

---

## Manifests

### Deployment

**Arquivo:** `k8s/app/deployment.yaml`

**Pontos principais:**
- Roda **2 réplicas** com estratégia `RollingUpdate` (zero downtime)
- `maxSurge: 1` — permite 1 pod extra durante o rollout
- `maxUnavailable: 1` — substitui 1 pod por vez
- Variável `APP_ENV` definida como `Production`
- `DB_USER` e `DB_PASSWORD` lidos de um `Secret` (nunca em plain text)
- **Requests e Limits** definidos para garantir QoS no cluster:

| Recurso | Request | Limit |
|---------|---------|-------|
| CPU     | 0.3     | 1.0   |
| Memória | 64Mi    | 256Mi |

- **livenessProbe** — reinicia o pod se a aplicação travar (GET `/` na porta 8080, falha após 3 tentativas)
- **readinessProbe** — remove o pod do balanceamento até estar pronto para receber tráfego (GET `/` na porta 8080)

**Como aplicar:**

```bash
kubectl apply -f k8s/app/deployment.yaml
```

**Verificar:**

```bash
kubectl get pods -n app
kubectl rollout status deployment/hubii-app -n app
```

---

### Service

**Arquivo:** `k8s/app/service.yaml`

**Pontos principais:**
- Tipo `ClusterIP` — expõe a aplicação internamente no cluster
- Porta `80` mapeada para `targetPort 8080` (porta da aplicação)
- Selector `app: app` — roteia tráfego apenas para os pods do deployment

**Como aplicar:**

```bash
kubectl apply -f k8s/app/service.yaml
```

**Verificar:**

```bash
kubectl get svc -n app
```

---

### Ingress

**Arquivo:** `k8s/app/ingress.yaml`

**Pontos principais:**
- Usa o `ingressClassName: nginx` (requer ingress-nginx instalado no cluster)
- Roteia requisições com `Host: app.hubii` e path `/app` para o service `hubii-app:80`
- Annotation `rewrite-target: /` remove o prefixo `/app` antes de encaminhar ao pod

**Como aplicar:**

```bash
kubectl apply -f k8s/app/ingress.yaml
```

**Verificar:**

```bash
kubectl get ingress -n app
```

**Testar (Kind/Minikube via NodePort):**

```bash
# Descobrir a porta do ingress controller
kubectl get svc -n ingress-nginx

# Testar com o Host header
curl -H "Host: app.hubii" http://localhost:<nodeport>/app
```

---

### Secret

**Arquivo:** `k8s/app/secret.yaml`

**Pontos principais:**
- Armazena `DB_USER` e `DB_PASSWORD` de forma separada dos manifestos de configuração
- Referenciado no Deployment via `secretKeyRef`

**Como aplicar:**

```bash
kubectl apply -f k8s/app/secret.yaml
```

> **Atenção:** Em produção, não versionar este arquivo com credenciais reais. Ver seção de Segurança.

---

## Ordem de aplicação recomendada

```bash
kubectl create namespace app

kubectl apply -f k8s/app/secret.yaml
kubectl apply -f k8s/app/deployment.yaml
kubectl apply -f k8s/app/service.yaml
kubectl apply -f k8s/app/ingress.yaml
```

---

## Verificação completa

```bash
# Pods rodando
kubectl get pods -n app

# Service e endpoints
kubectl get svc -n app
kubectl get endpoints -n app

# Ingress
kubectl describe ingress -n app

# Logs da aplicação
kubectl logs -n app -l app=app
```
