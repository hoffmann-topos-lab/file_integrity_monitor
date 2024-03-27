import hashlib
import os
import time
from datetime import datetime
import json

def ler_configuracoes(caminho_config='config.json'):
    with open(caminho_config, 'r') as arquivo_config:
        configuracoes = json.load(arquivo_config)
    return configuracoes


def calcular_hash_arquivo(caminho_arquivo):
    """Calcula o hash SHA-256 de um arquivo."""
    hasher = hashlib.sha256()
    with open(caminho_arquivo, 'rb') as f:
        conteudo = f.read()
        hasher.update(conteudo)
    return hasher.hexdigest()

def listar_arquivos_com_subdiretorios(diretorio):
    """Lista todos os arquivos em um diretório e seus subdiretórios."""
    arquivos = []
    for raiz, diretorios, arquivos_neste_diretorio in os.walk(diretorio):
        for nome_arquivo in arquivos_neste_diretorio:
            caminho_completo = os.path.join(raiz, nome_arquivo)
            arquivos.append(caminho_completo)
    return arquivos

def verificar_criar_diretorio_log():
    """Verifica e cria o diretório de logs se não existir."""
    diretorio_log = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(diretorio_log):
        os.makedirs(diretorio_log)
    return diretorio_log

def registrar_log(mensagem):
    """Registra uma mensagem de log com timestamp em um arquivo de log."""
    diretorio_log = verificar_criar_diretorio_log()
    arquivo_log = os.path.join(diretorio_log, "monitoramento_log.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(arquivo_log, "a") as log_file:
            log_file.write(f"{timestamp} - {mensagem}\n")
    except Exception as e:
        print(f"Erro ao registrar log: {e}")

def monitorar_integridade(diretorio, intervalo=60):
    """Monitora a integridade dos arquivos em um diretório."""
    estado_arquivos = {}

    # Salvar estado inicial dos arquivos
    for arquivo in listar_arquivos_com_subdiretorios(diretorio):

        estado_arquivos[arquivo] = calcular_hash_arquivo(arquivo)
    
    print("Iniciando monitoramento...")

    try:
        while True:
            for arquivo in listar_arquivos_com_subdiretorios(diretorio):
                hash_atual = calcular_hash_arquivo(arquivo)
                if arquivo not in estado_arquivos:
                    mensagem = f"Arquivo novo detectado: {arquivo}"
                    print(mensagem)
                    registrar_log(mensagem)
                    estado_arquivos[arquivo] = hash_atual
                elif estado_arquivos[arquivo] != hash_atual:
                    mensagem = f"Alteração detectada no arquivo: {arquivo}"
                    print(mensagem)
                    registrar_log(mensagem)
                    estado_arquivos[arquivo] = hash_atual
            time.sleep(intervalo)
    except KeyboardInterrupt:
        print("Monitoramento interrompido.")

# Exemplo de uso
if __name__ == "__main__":
    configuracoes = ler_configuracoes()  # Lê as configurações do arquivo de configuração padrão, 'config.json'
    diretorio_para_monitorar = configuracoes['diretorio_monitorado']  # Usa o diretório especificado no arquivo de configuração
    intervalo = configuracoes.get('intervalo_verificacao', 60)  # Usa um valor padrão caso a configuração não exista
    monitorar_integridade(diretorio_para_monitorar, intervalo)


