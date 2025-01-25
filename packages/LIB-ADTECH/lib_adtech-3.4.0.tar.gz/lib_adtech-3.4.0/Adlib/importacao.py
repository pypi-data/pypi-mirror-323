import functools
import inspect
import threading
from Adlib.api import *
from Adlib.funcoes import *
from pathlib import Path
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from time import sleep


tokenTelegram = '7502689321:AAHrPDp9Y-MsVhcTzh_OImoRZXJsOPNoNKk'
chat_id = '-794597825'


def checkEvent():
    """
    Decorator to check if an event is set before executing the decorated function.
    The event is dynamically retrieved from the function's arguments.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get the function's signature and parameter names
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            resetManager = bound_args.arguments.get("resetManager")
            
            if isinstance(resetManager, threading.Event):
                resetManager.set()

            # if isinstance(resetManager, threading.Event) and not resetManager.is_set():
            #     logging.warning(f"Event is not set. Skipping execution of {func.__name__}.")
            #     return None

            return func(*args, **kwargs)
        return wrapper
    return decorator


@checkEvent()
def importacaoVirtaus(virtaus: Chrome, filepath: Path, nomeBanco: str, enumBanco: EnumBanco, options: dict, resetManager: threading.Event = None) -> int:
    
    putStatusRobo(EnumStatus.LIGADO, EnumProcesso.IMPORTACAO, enumBanco)
    
    portabilidade = options.get("portabilidade", False)
    layout = options.get("layout", False)
    empty = options.get("empty", False)

    if empty:
        putStatusRobo(EnumStatus.SEM_PROPOSTA, EnumProcesso.IMPORTACAO, enumBanco)

    else:
        while True:
            putStatusRobo(EnumStatus.IMPORTANDO, EnumProcesso.IMPORTACAO, enumBanco)
            
            try:
                if resetManager:
                    if not resetManager.is_set():   # Finaliza o bot
                        virtaus.quit()
                        return 1

                virtaus.get('https://adpromotora.virtaus.com.br/portal/p/ad/pageworkflowview?processID=ImportacaoArquivoEsteira')
                sleep(10)
                aguardarAlert(virtaus)
                
                sleep(5)
                iframe = virtaus.find_elements('tag name','iframe')[0]
                virtaus.switch_to.frame(iframe)

                # Banco
                clickarElemento(virtaus, '/html/body/div/form/div/div[1]/div[2]/div/div[1]/span/span[1]/span/ul/li/input').click()
                esperarElemento(virtaus, '/html/body/div/form/div/div[1]/div[2]/div/div[1]/span/span[1]/span/ul/li/input').send_keys(nomeBanco)
                sleep(5)
                esperarElemento(virtaus, '/html/body/div/form/div/div[1]/div[2]/div/div[1]/span/span[1]/span/ul/li/input').send_keys(Keys.ENTER)

                # Layout
                if layout:
                    try:
                        dropdown = esperarElemento(virtaus, '//*[@id="selectLayout"]')
                        select = Select(dropdown)
                        try:
                            select.select_by_visible_text(layout)
                        except Exception as e:
                            print(f"Error selecting option: {e}")
                    except:
                        print(f"Input de Layout não encontrado")

                # Portabilidade
                if portabilidade:
                    try:
                        dropdown = esperarElemento(virtaus, '//*[@id="selectPortabilidade"]')
                        select = Select(dropdown)
                        try:
                            select.select_by_visible_text(portabilidade)
                        except Exception as e:
                            print(f"Error selecting option: {e}")
                            
                    except Exception as e:
                        print(f"Error selecting option: {e}")
                        print(f"Input de portabilidade não encontrado")

                virtaus.switch_to.default_content()          

                clickarElemento(virtaus, '//*[@id="tab-attachments"]/a/span').click()
                sleep(5)
                esperarElemento(virtaus, '//*[@id="lb-input-upload"]')
                
                fileInput = virtaus.find_element('xpath', '//*[@id="ecm-navigation-inputFile-clone"]')
                fileInput.send_keys(str(filepath))
                sleep(3)
                
                # Upload arquivo
                clickarElemento(virtaus, '//*[@id="workflowActions"]/button[1]').click()
                sleep(5)

                os.remove(str(filepath))
                elemento = esperarElemento(virtaus, '/html/body/div[1]/div[3]/div/div/div[2]/div/div/div/div[3]/div[1]/div/div[1]/span/a')
                numeroSolicitacao = elemento.text

                putTicket(numeroSolicitacao, EnumProcesso.IMPORTACAO, enumBanco)
                mensagem = f"Importação Efetuada: <b> {nomeBanco} - {numeroSolicitacao}</b> ✅"
                
                if resetManager:
                    resetManager.set()              # Reseta countdown de restart do bot

                mensagemTelegram(tokenTelegram, chat_id, mensagem)
                putStatusRobo(EnumStatus.LIGADO, EnumProcesso.IMPORTACAO, enumBanco)
                return 0

            except Exception as e:
                print(e)
                print('Erro ao tentar importar no Virtaus')
                putStatusRobo(EnumStatus.ERRO, EnumProcesso.IMPORTACAO, enumBanco)