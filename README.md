# DBFlow
O DBFlow é um pacote que usa o watchdogs para iniciar diversos tipos de serviço, como orquestramento de fluxo de carga, leitura de controle de diretórios, e execuçao de processos.
Com sua capacidade de lidar com execução paralela e logging robusto, este pacote é perfeito para ambientes que necessitam de processamento de dados ágil e confiável.

## Características

- Monitoramento em tempo real de diretórios para disparo de tarefas de pipeline de dados.
- Execução assíncrona de múltiplas tarefas, agrupadas por configurações definidas pelo usuário para execução paralela.
- Logging detalhado para rastreamento e auditoria de todas as tarefas executadas.
- Configuração flexível de grupos de tarefas para maximizar a eficiência do processamento paralelo.
- Gestão de tarefas orientada por eventos, permitindo respostas dinâmicas com base em atividades específicas do diretório.

## Autor

**Dayvid Borges de Lima** - Desenvolvedor e mantenedor do projeto. 

Para qualquer dúvida ou feedback, sinta-se à vontade para entrar em contato através do [GitHub](https://github.com/dayvidborges).

## Dependências

Este pacote utiliza várias bibliotecas Python para a manipulação eficiente de eventos do sistema de arquivos e gerenciamento de tarefas:

- `watchdog` para a funcionalidade de observação de diretório.
- `concurrent.futures` para a execução concorrente de tarefas.
- `subprocess` para iniciar os scripts que compõem as tarefas do pipeline.
- Bibliotecas padrão como `os`, `sys`, `re` e `uuid` para várias funcionalidades auxiliares.

## Instalação

Use o seguinte comando para instalar as dependências necessárias:

```bash
pip install watchdog
```

Após a instação das dependências clone o repositório para a pasta do seu projeto

```bash
git clone https://github.com/dayvidborges/DBFlow.git
```

caso seu projeto utilize diversos diretórios será necessario apendar a pasta do sistema em que o repositorio foi clonado

```python
import sys
sys.path.append('caminho/para/a/pasta/do/repositorio/')
from dbflow import PyPelineWatcher
# Ou
from dbflow import *
```

após clone o repositorio
## Configuração e Uso
A configuração do seu ambiente com o PyPelineWatcher é um processo simples, delineado nos seguintes passos:

1. **Definição do Pipeline**: Configure seu pipeline de tarefas específicas, incluindo caminhos de script, identificadores de grupo para tarefas paralelas e caminhos para logs.

   - **Exemplo:**
   ```Python
        logPath1 = 'caminho/logFolder1'
        logPath2 = 'caminho/logFolder2'
        logPath3 = 'caminho/logFolder3'
        logPath4 = 'caminho/logFolder4'
        PIPELINE = {
            'test':[
                (
                    '/home/user/Documentos/Projects/testes/teste_001/src/python/test.py',
                    '1',
                    logPath1,
                ),
                (
                    '/home/user/Documentos/Projects/testes/teste_001/src/python/test2.py',
                    '1',
                    logPath2,
                ),
            ],
            'test2':[
                (
                    '/home/user/Documentos/Projects/testes/teste_001/src/python/test.py',
                    '1',
                    logPath3,
                ),
                (
                    '/home/user/Documentos/Projects/testes/teste_001/src/python/test2.py',
                    '1',
                    logPath4,
                ),
            ],
        }
   ```
2. **Inicialização do Watcher**: Estabeleça um `PyPelineWatcher` para começar a monitorar o diretório especificado e suas subpastas, se necessário.

   - **Exemplo:**
   ```Python
    folderToWatchPath = 'caminho/para/pasta/a/observar'
    watcher = PyPelineWatcher()
    watcher.startWatcher(folderToWatchPath,pipeline=PIPELINE)
   ```
4. **Manipulação de Eventos**: Determine como os eventos do sistema de arquivos são tratados, iniciando tarefas relevantes conforme necessário.
5. **Execução e Logging**: Execute tarefas de forma síncrona ou assíncrona, com detalhes completos de cada execução gravados em arquivos de log.
    - **NOTA IMPORTANTE**: A execução do fluxo vai acontecer de acordo com as tags definidas no pipeline, no ex acima temos as tags 'test' e 'test2';
      que representam o controle de arquivos naquele fluxo de processo python, por ex, se um arquivo que tenha o nome test ou test2 entrar na pasta que está sendo observada,
      ele vai iniciar os fluxos de ETL test.py e test2.py, note que nesse exemplo se voce inserir um arquivo que contenha o nome teste2 ele vai executar tanto o taskgroup da
      tag test quanto o taskgroup da tag test2 pois test esta contido em test2. **ATENÇÃO AO NOMEAR AS TAGS**

     - **NOTA SOBRE EXECUÇÃO**: Dentro do pipeline nos temos a tag e uma lista contendo uma tupla de 3 indices, onde-
         * Indíce[0]: Representa o caminho para o arquivo python a ser executado;
         * Indíce[1]: Representa o Grupo da task, **VEJA EXPLICAÇÃO ABAIXO SOBRE GRUPO**;
         * Indíce[2]: Representa o caminho para a pasta onde será armazenado o log daquela task;

     - **NOTA SOBRE GRUPOS**: Geralmente as tasks sao executadas pela ordem em que aparecem no pipeline, porém se voce definir duas tasks com o msm numero de grupo,
         o processo executará todas as tasks do grupo ao msm tempo de forma assíncrona

## Contribuições
Contribuições, problemas e solicitações de funcionalidades são bem-vindos. Este projeto adota um código de conduta e espera-se que os colaboradores o sigam. Por favor, consulte a documentação sobre como começar.

## Licença
Este projeto está licenciado sob a Licença GNU GPLv3 - veja o arquivo [LICENSE](https://github.com/dayvidborges/DBFlow/blob/main/LICENSE) para detalhes.

