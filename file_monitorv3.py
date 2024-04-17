import hashlib
import os
import time
from datetime import datetime
import json
import threading
import logging
import sqlite3
import urllib.parse
import base64


# Configurações básicas de logging antes de definir o diretório para evitar log no diretório incorreto
DIRETORIO_LOGS = os.path.join(os.getcwd(), "logs")
if not os.path.exists(DIRETORIO_LOGS):
    os.makedirs(DIRETORIO_LOGS, exist_ok=True)
ARQUIVO_LOG = os.path.join(DIRETORIO_LOGS, "monitoramento_log.txt")
ARQUIVO_DB = os.path.join(os.getcwd(), 'arquivos_estado.db')
logging.basicConfig(level=logging.INFO, filename=ARQUIVO_LOG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')



def conectar_db():
    return sqlite3.connect(ARQUIVO_DB)

def criar_tabela():
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estados (
                caminho TEXT PRIMARY KEY,
                hash TEXT NOT NULL,
                timestamp REAL
            )
        ''')
        conn.commit()

def atualizar_ou_inserir_arquivo(caminho_arquivo, hash_arquivo):
    if caminho_arquivo not in [ARQUIVO_LOG, ARQUIVO_DB]:
        with conectar_db() as conn:
            cursor = conn.cursor()
            timestamp = os.path.getmtime(caminho_arquivo)
            cursor.execute('''
                INSERT INTO estados (caminho, hash, timestamp) VALUES (?, ?, ?)
                ON CONFLICT(caminho) DO UPDATE SET hash=excluded.hash, timestamp=excluded.timestamp
            ''', (caminho_arquivo, hash_arquivo, timestamp))
            conn.commit()



def ler_configuracoes(caminho_config='config.json'):
    try:
        with open(caminho_config, 'r') as arquivo_config:
            configuracoes = json.load(arquivo_config)

        # Obtendo o diretório monitorado e decodificando possíveis codificações
        diretorio_monitorado = configuracoes.get('diretorio_monitorado', os.getcwd())
        diretorio_monitorado = urllib.parse.unquote(diretorio_monitorado)  # Desfazendo codificações percentuais

        # Normalize o caminho para resolver qualquer obscuração como /./ ou /../
        diretorio_monitorado_normalizado = os.path.normpath(diretorio_monitorado)

        # Verifique se o caminho normalizado ainda contém elementos de navegação para cima
        if any(part in ["..", "../"] for part in diretorio_monitorado_normalizado.split(os.sep)):
            logging.error(f"Tentativa de path traversal detectada no caminho: {diretorio_monitorado_normalizado}")
            return {'diretorio_monitorado': os.getcwd(), 'intervalo_verificacao': 60}

        # Convertendo para caminho absoluto para garantir segurança
        diretorio_monitorado_absoluto = os.path.abspath(diretorio_monitorado_normalizado)

    except FileNotFoundError:
        logging.error(f"Não foi possível encontrar o arquivo de configuração: {caminho_config}. Importando configurações padrão.")
        return {'diretorio_monitorado': os.getcwd(), 'intervalo_verificacao': 60}
    except json.JSONDecodeError:
        logging.error(f"Erro ao decodificar o arquivo JSON: {caminho_config}. Importando configurações padrão.")
        return {'diretorio_monitorado': os.getcwd(), 'intervalo_verificacao': 60}
    except Exception as e:
        logging.error(f"Erro ao ler o arquivo de configuração {caminho_config}: {e}. Importando configurações padrão.")
        return {'diretorio_monitorado': os.getcwd(), 'intervalo_verificacao': 60}

    return {'diretorio_monitorado': diretorio_monitorado_absoluto, 'intervalo_verificacao': configuracoes.get('intervalo_verificacao', 60)}




def calcular_hash_arquivo(caminho_arquivo):
    hasher = hashlib.sha256()
    try:
        with open(caminho_arquivo, 'rb') as f:
            for bloco in iter(lambda: f.read(4096), b""):
                hasher.update(bloco)
        return hasher.hexdigest()
    except FileNotFoundError:
        logging.error(f"Arquivo não encontrado: {caminho_arquivo}")
    except PermissionError:
        logging.error(f"Permissão negada ao tentar ler o arquivo: {caminho_arquivo}")
    except IOError as e:
        logging.error(f"Erro de I/O ao ler o arquivo {caminho_arquivo}: {e}")
    return None

def carregar_estado_anterior():
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT caminho, hash FROM estados")
        return {row[0]: row[1] for row in cursor.fetchall()}

def monitorar_integridade(diretorio, thread_stop_event, intervalo=60):
    estado_anterior = carregar_estado_anterior()
    estado_inicial_carregado = bool(estado_anterior)  # Verifica se o estado anterior não está vazio

    while not thread_stop_event.is_set():
        estado_atual = {}
        for raiz, _, arquivos_neste_diretorio in os.walk(diretorio):
            for nome_arquivo in arquivos_neste_diretorio:
                caminho_completo = os.path.join(raiz, nome_arquivo)
                if caminho_completo not in [ARQUIVO_LOG, ARQUIVO_DB]:
                    hash_arquivo = calcular_hash_arquivo(caminho_completo)
                    if hash_arquivo:
                        estado_atual[caminho_completo] = hash_arquivo
                        if caminho_completo not in estado_anterior:
                            atualizar_ou_inserir_arquivo(caminho_completo, hash_arquivo)
                            if estado_inicial_carregado:  # Registra como novo apenas se o estado inicial estava carregado
                                logging.info(f"Arquivo novo detectado: {caminho_completo}")
                        elif estado_anterior.get(caminho_completo) != hash_arquivo:
                            atualizar_ou_inserir_arquivo(caminho_completo, hash_arquivo)
                            logging.info(f"Modificação detectada no arquivo: {caminho_completo}")

        estado_anterior = estado_atual.copy()
        time.sleep(intervalo)

if __name__ == "__main__":
    criar_tabela()
    configuracoes = ler_configuracoes()
    diretorio_para_monitorar = configuracoes.get('diretorio_monitorado', os.getcwd())
    intervalo = configuracoes.get('intervalo_verificacao', 60)
    thread_stop_event = threading.Event()
    monitor_thread = threading.Thread(target=monitorar_integridade, args=(diretorio_para_monitorar, thread_stop_event, intervalo))
    monitor_thread.start()

    print("Digite 'Exit' para interromper o monitoramento:")
    while True:
        user_input = input().lower()
        if user_input == "exit":
            print("Finalizando o monitoramento...")
            thread_stop_event.set()
            monitor_thread.join()
            print("Monitoramento encerrado.")
            break
        else:
            print("Comando inválido. Digite 'Exit' para interromper o monitoramento:")
