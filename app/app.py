import psycopg2
import redis
from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics


app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.start_http_server(9999)

@app.route("/")
def hello_world():
    return "App on"

@app.route('/redis')
def get_status_redis():
    try:
        # conecte-se ao Redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        # verifique se a conexão foi estabelecida
        r.ping()
        
        # retorne uma mensagem indicando que a conexão foi bem-sucedida
        return "Conexão com o Redis estabelecida com sucesso!"
    except:
        # retorne uma mensagem indicando que a conexão falhou
        return "Falha ao conectar com o Redis."


@app.route('/postgres')
def get_status_postgres():
    try:
        # conecte-se ao PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="senhafacil"
        )
        
        # feche a conexão com o PostgreSQL
        conn.close()
        
        # retorne uma mensagem indicando que a conexão foi bem-sucedida
        return "Conexão com o PostgreSQL estabelecida com sucesso!"
    except Exception as e:
        # retorne uma mensagem indicando que a conexão falhou
        return "Falha ao conectar com o PostgreSQL."

@app.route('/error')
def get_error():
    # simule um erro 500
    error_message = "Ocorreu um erro interno no servidor."
    return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug = True)
