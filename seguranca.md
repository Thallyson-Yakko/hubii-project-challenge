# Parte 6 – Segurança

## Gerenciamento de Segredos em Produção

### AWS Secrets Manager + External Secrets Operator

Em produção, segredos nunca devem ser armazenados em arquivos versionados ou variáveis de ambiente em plain text. A abordagem recomendada é usar o **External Secrets Operator (ESO)** integrado ao **AWS Secrets Manager**.

**Como funciona:**
1. O segredo é criado e versionado no AWS Secrets Manager
2. O ESO é instalado no cluster e autenticado via **IRSA (IAM Role for Service Accounts)**
3. Um recurso `ExternalSecret` no Kubernetes sincroniza o segredo do AWS para um `Secret` nativo do Kubernetes
4. O pod lê o `Secret` normalmente via `secretKeyRef`

```yaml
# Exemplo de ExternalSecret
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-secret
  namespace: app
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-store
    kind: ClusterSecretStore
  target:
    name: db-secret
  data:
    - secretKey: DB_USER
      remoteRef:
        key: hubii/app/db
        property: username
    - secretKey: DB_PASSWORD
      remoteRef:
        key: hubii/app/db
        property: password
```

**Vantagens:**
- Segredos nunca entram no repositório git
- Rotação automática de credenciais
- Auditoria de acesso via AWS CloudTrail
- Controle fino de quem acessa qual segredo via IAM

---

## Como Evitar Exposição de Credenciais

- **Nunca commitar secrets no git** — adicionar `secret.yaml` com valores reais ao `.gitignore`
- **Usar `.gitignore`** para bloquear arquivos sensíveis:
  ```
  **/secret.yaml
  **/*.env
  .env*
  ```
- **Escanear o repositório** com ferramentas como `git-secrets`, `truffleHog` ou `gitleaks` no pipeline de CI para detectar credenciais acidentalmente commitadas
- **Nunca usar `latest` como tag de imagem** em produção — garante rastreabilidade e evita pulls inesperados
- **Variáveis de ambiente sensíveis** sempre via `secretKeyRef`, nunca `value: senha123`

---

## Segurança da Imagem Docker

### Multi-stage Build

Usar multi-stage build reduz drasticamente o tamanho da imagem e elimina ferramentas de build que poderiam ser exploradas:

```dockerfile
# Stage 1: build/dependências
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: imagem final enxuta
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ .
RUN adduser --disabled-password --gecos "" app_user
USER app_user
EXPOSE 8080
CMD ["python", "app.py"]
```

### Imagens Distroless

Para máxima redução de superfície de ataque, usar imagens **distroless** (sem shell, sem package manager, sem utilitários do SO):

```dockerfile
FROM gcr.io/distroless/python3-debian12
COPY --from=builder /app /app
CMD ["/app/app.py"]
```

**Benefícios:**
- Sem shell = sem execução de comandos arbitrários em caso de RCE
- Tamanho drasticamente menor
- Menos CVEs por ter menos pacotes instalados

### Boas Práticas Gerais de Imagem

- Escanear imagens com `Trivy` ou `Snyk` no pipeline de CI
- Nunca rodar como `root` — sempre criar e usar um usuário não-privilegiado
- Fixar versões de dependências no `requirements.txt` para builds reproduzíveis
- Usar imagens base oficiais e verificadas

---

## Acesso Mínimo Privilegiado em Ambientes Cloud

### IRSA (IAM Roles for Service Accounts) — AWS

Ao invés de usar credenciais AWS estáticas (Access Key/Secret Key) dentro dos pods, usar **IRSA** vincula uma IAM Role diretamente a uma Service Account do Kubernetes. O pod assume a role automaticamente via OIDC, sem nenhuma credencial armazenada:

```bash
# Criar service account vinculada à IAM Role
kubectl annotate serviceaccount app-sa \
  eks.amazonaws.com/role-arn=arn:aws:iam::123456789:role/hubii-app-role \
  -n app
```

### OIDC no Pipeline de CI/CD

Para o pipeline (GitHub Actions, GitLab CI) publicar imagens ou fazer deploy sem guardar credenciais:

```yaml
# GitHub Actions com OIDC para AWS
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/github-actions-role
    aws-region: us-east-1
```

**Vantagens do OIDC no pipeline:**
- Zero credenciais armazenadas como secrets no CI
- Token temporário gerado por execução
- Escopo limitado à role assumida

### Princípio do Menor Privilégio

- IAM Roles com apenas as permissões necessárias (ex: role do app só lê secrets específicos no Secrets Manager)
- `NetworkPolicy` no Kubernetes para limitar comunicação entre namespaces e pods
- `PodSecurityContext` para restringir capabilities do container:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

---

## Resumo das Práticas Adotadas Neste Projeto

| Prática | Status |
|---------|--------|
| Credenciais via Secret (não plain text) | Aplicado |
| Usuário não-root na imagem Docker | Aplicado |
| Requests/Limits definidos | Aplicado |
| Liveness e Readiness probes | Aplicado |
| Tag de imagem fixada (`:1.1`) | Aplicado |
| External Secrets + AWS Secrets Manager | Recomendado para produção |
| Multi-stage / Distroless | Recomendado para produção |
| OIDC no pipeline | Recomendado para produção |
| Scan de imagem (Trivy) | Recomendado para produção |
| NetworkPolicy | Recomendado para produção |
