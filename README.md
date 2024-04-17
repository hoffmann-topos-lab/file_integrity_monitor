# Monitoramento de Integridade de Arquivos

## Descrição
Este projeto é uma ferramenta de monitoramento de integridade de arquivos projetada para detectar e registrar alterações em arquivos dentro de um diretório especificado e seus subdiretórios. Ele calcula e compara os hashes SHA-256 de arquivos para identificar modificações.

## Atualizações

-Implementação de Threading:
A nova versão utiliza threading para permitir que o monitoramento continue rodando em um plano de fundo separado, melhorando a usabilidade do script sem bloquear a entrada do usuário.

-Uso de SQLite para Persistência de Dados:
Os estados dos arquivos agora são armazenados em um banco de dados SQLite. Isso melhora a eficiência na verificação de mudanças e permite uma recuperação de estado mais robusta entre as execuções do script.

-Melhorias no Sistema de Logging:
A configuração de logging foi aprimorada para utilizar o módulo logging do Python, o que proporciona uma gravação de logs mais estruturada e fácil de filtrar, utilizando níveis de severidade e um formato de mensagem padronizado.

-Verificações de Segurança na Leitura de Configurações:
Foram adicionadas verificações para prevenir ataques de path traversal ao normalizar e resolver caminhos de diretórios obtidos a partir do arquivo de configuração. Além disso, agora o script trata exceções relacionadas à leitura do arquivo de configuração, garantindo que o script não falhe inesperadamente.

Leitura Eficiente de Arquivos:
A função calcular_hash_arquivo foi modificada para ler o arquivo em blocos, o que reduz o uso de memória em arquivos grandes e trata exceções de arquivo não encontrado, permissão negada, e erros de I/O, registrando adequadamente nos logs.

## Recursos
- Monitoramento de arquivos em tempo real.
- Registro de todas as alterações detectadas em um arquivo de log.
- Capacidade de monitorar subdiretórios de forma recursiva.

## Pré-requisitos
- Python 3.6 ou superior.

## Como Configurar

Siga estas etapas para configurar e iniciar o monitoramento de integridade de arquivos em seu sistema:

1. **Clone o repositório**:
   - Clone este repositório para o seu sistema local usando o comando:
     ```
     git clone https://github.com/hoffmann-topos-lab/file_integrity_monitor
     ```

2. **Navegue até o diretório do projeto**:
   - Mude para o diretório do projeto clonado:
     ```
     cd file_integrity_monitor
     ```

3. **Certifique-se de que o Python está instalado**:
   - Verifique se o Python está instalado e configurado corretamente em seu sistema executando:
     ```
     python --version
     ```
   - Você deverá ver a versão do Python que está instalada.

4. **Modifique o arquivo de configuração**:
   - No diretório do projeto, modifique o arquivo `config.json`. Preencha-o com as configurações iniciais necessária.
   - Substitua os valores conforme necessário para refletir o diretório que você deseja monitorar, o intervalo de verificação em segundos e o caminho desejado para os logs de monitoramento.


Seguindo essas etapas, você configurará o ambiente necessário para rodar o script de monitoramento de integridade de arquivos no seu sistema.


## Como Executar
Para iniciar o monitoramento, execute o script da seguinte maneira:

  `python monitoramento_arquivos.py /caminho/para/diretorio`

Substitua `/caminho/para/diretorio` pelo caminho do diretório que você deseja monitorar.

## Estrutura do Projeto
- `monitoramento_arquivos.py`: O script principal que executa o monitoramento de arquivos.
- `logs/`: Diretório onde os arquivos de log serão salvos.

## Logs
Os logs de monitoramento são gravados no diretório `/logs/`, com informações sobre cada arquivo alterado, incluindo o nome do arquivo, o caminho e o timestamp da detecção da alteração.

## Execução em Background

Para executar o script em background em sistemas Unix/Linux, você pode usar o comando `nohup` ou `screen` para iniciar o script e permitir que ele continue rodando após o fechamento do terminal:

  `nohup python3 monitoramento_arquivos.py /caminho/para/diretorio &`


Ou, usando `screen`:

  `screen -dm python3 monitoramento_arquivos.py /caminho/para/diretorio`


Para retornar à sessão `screen`, use `screen -r`.

## Execução em Background no Windows

Para executar o script em background no Windows, você pode utilizar o Agendador de Tarefas para agendar a execução do script ou executá-lo diretamente com o PowerShell.

### Usando o PowerShell

Você pode usar o PowerShell para executar o script em background. Abra o PowerShell e execute:

  `Start-Process python -ArgumentList "caminho\para\monitoramento_arquivos.py", "caminho\para\diretorio" -WindowStyle Hidden`


Substitua `caminho\para\monitoramento_arquivos.py` e `caminho\para\diretorio` pelos caminhos apropriados no seu sistema.

### Agendador de Tarefas

1. Abra o Agendador de Tarefas e clique em "Criar Tarefa...".
2. Na aba "Geral", insira um nome para a tarefa.
3. Na aba "Ações", clique em "Novo..." e configure a ação para iniciar um programa. No campo "Programa/script", insira o caminho para o executável do Python. No campo "Adicionar argumentos (opcional)", insira o caminho completo para o script e o diretório que deseja monitorar, separados por espaço.
4. Na aba "Disparadores", configure quando você deseja que o script seja executado (por exemplo, na inicialização do sistema ou em um horário específico).

### Agendamento com Task Scheduler (Agendador de Tarefas)

Para usuários que preferem uma interface gráfica, o Agendador de Tarefas do Windows pode ser usado para configurar o script para ser executado automaticamente em intervalos definidos:

1. Pressione `Windows+R`, digite `taskschd.msc` e pressione Enter para abrir o Agendador de Tarefas.
2. Clique em "Criar Tarefa..." no painel da direita.
3. Na aba "Geral", dê um nome para a sua tarefa.
4. Vá para a aba "Triggers" e clique em "Novo..." para definir quando a tarefa deve ser iniciada.
5. Na aba "Ações", clique em "Novo..." e configure a ação para iniciar o script Python. No campo "Programa/script", digite o caminho para o Python. No campo "Adicionar argumentos", insira o caminho do seu script e o diretório a ser monitorado.
6. Configure quaisquer outras opções desejadas e clique em "OK" para salvar a tarefa.

Lembre-se, ao configurar tarefas no Windows, você precisará saber o caminho para o executável do Python em seu sistema, que pode ser encontrado executando `where python` no prompt de comando, se Python foi adicionado ao PATH durante a instalação.



## Configuração com Cronjob

Se preferir agendar a execução do script em intervalos regulares em vez de rodá-lo continuamente, você pode configurar um cronjob.

1. Abra o crontab para edição:

  `crontab -e`


2. Adicione uma linha para agendar a execução do seu script. Por exemplo, para executar o script todos os dias à meia-noite, adicione:

  `0 0 * * * /usr/bin/python3 /caminho/completo/para/monitoramento_arquivos.py /caminho/para/diretorio`

  
3. Substitua `/usr/bin/python3` e `/caminho/completo/para/monitoramento_arquivos.py` pelos caminhos apropriados em seu sistema.

Lembre-se de que ao usar cronjob, o script será iniciado e terminará com base no agendamento, então considere suas necessidades de monitoramento ao escolher entre execução contínua em background ou execução periódica via cron.



## Atualizações Futuras
- **Notificações por E-mail**: Implementar notificações por e-mail para alertar os usuários sobre alterações detectadas.
- **Interface de Usuário**: Desenvolver uma interface de usuário web para facilitar o monitoramento e a revisão dos logs de alterações.

## Considerações Adicionais de Segurança

- Permissões de Arquivos e Diretórios:
Certifique-se de que o script e o diretório de logs tenham as permissões corretas para prevenir acesso não autorizado. O script não deve ter permissões de administrador a menos que estritamente necessário.

-Validação e Sanitização de Inputs:
Embora já hajam algumas soluções contra SLQi e Path Traversal, é crucial validar e sanitizar todas as entradas do usuário e dos arquivos de configuração para prevenir injeções e outras vulnerabilidades.

-Atualizações e Patches:
Mantenha todas as bibliotecas e o próprio Python atualizados com as últimas correções de segurança para mitigar vulnerabilidades conhecidas.


## Contribuindo
Sinta-se à vontade para contribuir com o projeto. Você pode enviar pull requests ou abrir issues para discutir melhorias ou adicionar novas funcionalidades.

## Licença
Este projeto é licenciado sob a [Licença GLP3](LICENSE). Consulte o arquivo `LICENSE` no repositório para obter mais detalhes.

