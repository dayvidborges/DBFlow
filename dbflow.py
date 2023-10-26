import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
from concurrent.futures import ThreadPoolExecutor
import re
from pathlib import Path
import os 
import sys 
import uuid
from datetime import datetime 

# --PYPELINE
class PyPelineTaskManager():
    """
    Classe responsável por gerenciar as tasks do pipeline de dados, recebe um dicionario com a estrutura do pipeline
    e executa os processos com suas dependencias.
    
    Estrutura do pipeline dentro do dicionario: 
    {tag_1:(task1Path,group,logFilePath)}
    
    tag_1 : Recebe a tag do arquivo que vai sensibilizar a classe, quando algum arquivo que tenha essa tag no nome entrar no diretório que está sendo observado, vai iniciar a execução dos arquivos
    python, que deveria conter o ETL do arquivo.
    
    task1Path: Caminho do arquivo .py que vai executar aquela task
    
    group: Grupo que a task pertence, o uso de grupos é usado para executar tasks assincronamente, por padrao, o programa vai executar as tasks na ordem que elas aparecem na lista,
    porem se voce definir que duas ou mais tasks tem o msm grupo elas vao executar ao msm tempo.
    
    logFilePath: Caminho da pasta onde as logs dessa task vao ser armazenadas.
    
    Exemplo de pipeline:(
        PIPELINE = {
            'test':[
                (
                    '/home/user/Documentos/Projects/testes/teste_001/src/python/test.py',
                    '1',
                    LOGS,
                ),
                (
                    '/home/user/Documentos/Projects/testes/teste_001/src/python/test2.py',
                    '1',
                    LOGS,
                ),
            ],
            'test2':[
                (
                    '/home/user/Documentos/Projects/testes/teste_001/src/python/test.py',
                    '1',
                    LOGS,
                ),
                (
                    '/home/user/Documentos/Projects/testes/teste_001/src/python/test2.py',
                    '1',
                    LOGS,
                ),
            ],
        }
    )
    """
    def __init__(self) -> None:
        self.stoprun =  False
        self.pipeline = []
        self.tasksToRun = []
    def startProcess(self,pipeline,tasksKey):
        """
        Inicia a execução do pipeline de processos.

        Args:
            pipeline (dict): dicionario contendo a tagKey do fluxo de processos, e os arguemtnos dos processos
            tasksKey (_type_): chave que define qual fluxo iniciar

        Returns:
            _type_: _description_
        """
        self.pipeline = pipeline
        self.tasksToRun = self.pipeline[tasksKey].copy()
        runnedtasks = []
        self.stoprun = False
        
        def recursiveProcess():
            if not self.stoprun:
                processArgs = self.tasksToRun[0]
                groups = [args[1] for args in self.tasksToRun]
                currentProcessGroup = [index for index,value in enumerate(groups) if value == processArgs[1]]
                currentProcessTasks = [task for index,task in enumerate(self.tasksToRun) if index in currentProcessGroup]
                processId = str(uuid.uuid4())
                def startTask(currentProcessParams):
                    taskId = str(uuid.uuid4())
                    pythonFilePath = currentProcessParams[0]
                    logFileFolder = currentProcessParams[2]
                    now =  datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    logName = taskId+'_'+now+'.txt'
                    logFilePath = os.path.join(logFileFolder,logName)
                    Path(logFileFolder).mkdir(exist_ok=True)              
                            
                    process = subprocess.run(['python3',pythonFilePath],stdout=open(logFilePath,'w'))
                    runnedtasks.append((currentProcessParams,taskId))
                    self.tasksToRun.remove(currentProcessParams)
                    return (taskId,process)
                
                if len(currentProcessGroup) > 1:
                    def startConcurrentProcess(tasks):
                        with ThreadPoolExecutor(max_workers=5) as executor:
                            results = executor.map(startTask,tasks)
                            
                            for result in results:
                                if result[1].returncode > 0:
                                    self.stoprun = True
                    startConcurrentProcess(currentProcessTasks)
                    
                elif len(currentProcessGroup) ==  1:
                    task = currentProcessTasks[0]
                    taskResponse = startTask(task)
                    if taskResponse[1].returncode > 0:
                        self.stoprun = True
                
                if len(self.tasksToRun) == 0:
                    self.stoprun = True
                else:
                    recursiveProcess()
        recursiveProcess()      

class PyPelineHandler(FileSystemEventHandler,PyPelineTaskManager):    
    """
    O handler herda as classes FileSystemEventHandler e PyPelineTaskManager, 
    FileSystemEventHandler é uma classe do pacote watchdogs que é o sensor do diretório usado no projeto.
    """
    def __init__(self,pipeline=None,action=None) -> None:
        super().__init__()
        self.pipeline = pipeline
        self.action = action
    def on_created(self, event):
        if not event.is_directory:
            filePath = event.src_path
            try:
                fileName = str(filePath).split('/')[-1]
            except:
                fileName = filePath
            flag = False
            
            if not self.pipeline:
                raise ValueError('Nenhum Pipeline adicionado.')
            
            for key,tasks in self.pipeline.items():
                if key in fileName:
                    self.startProcess(self.pipeline,key)
                    flag = True
            if not flag:
                
                if not self.action:
                    now =  datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    print(
                        f"""
                        Arquivo: {filePath}
                        Ação: Nenhuma
                        Descrição: Nenhuma ação tomada
                        Timestamp: {now}
                        """
                    )
                elif self.action.upper() == 'DELETE':
                    os.remove(filePath)
                    now =  datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    print(f"""
                          Arquivo: {filePath}
                          Ação: Deletado
                          Timestamp: {now}
                          """
                    )
                           
class PyPelineWatcher():
    """
    O watcher é responsável por observar a pasta sensibilizada, o engine usado para leitura foi o watchdogs
    ele recebe o pipeline que é passado pelo PyPelineHandler ao PypelineTaskManager onde executará os processos:
    
    Essa classe contem o methodo startWatcher que deve ser usada para dar start ta engine.
    """
    def __init__(self) -> None:
        self.observer = Observer()
        self.path = ''
        
    def startWatcher(self,path,rec=False,wait=20,pipeline=None):
        """
        Função de start

        Args:
            path (str): Caminho para a pasta que vai ser observada
            rec (bool, optional): Se definido como True observa os subfolders da pasta especificada, se False ignora todos os arquivos do tipo pasta. Defaults to False.
            wait (int, optional): Espera na execução do observador. Defaults to 20.
            pipeline (_type_, optional): dicionario contendo a estrutura . Defaults to None.
        """
        self.path = path
        self.observer.schedule(PyPelineHandler(pipeline),self.path,recursive=rec)
        self.observer.start()
        try:
            while True:
                time.sleep(wait)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()
          