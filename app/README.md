# onboarding-sre

### Requisitos 

```
Instale na sua maquina python3 e o pip3

```

```
git clone <projeto>
cd app
python3 -m venv .
source ./bin/activate
```

### Instalando todas as dependencias 

```
pip3 install --no-cache-dir -r requirements.txt
python app.py

```

### Acesse no browser na porta 5000 ou via curl

```
curl localhost:5000
curl localhost:5000/redis
curl localhost:5000/postgres
curl localhost:5000/error
curl localhost:9999/metrics

```


