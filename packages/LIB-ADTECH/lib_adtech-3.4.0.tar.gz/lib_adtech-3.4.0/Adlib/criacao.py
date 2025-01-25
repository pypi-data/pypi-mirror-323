from Adlib.api import EnumBanco
from Adlib.funcoes import *
from Adlib.logins import loginVirtaus
from time import sleep
from selenium.webdriver.common.keys import Keys
from pprint import pprint
from typing import Callable
from selenium.webdriver import ChromeOptions
from dataclasses import dataclass
from Adlib.virtaus import *


@dataclass
class CriacaoUsuarioOptions:
    email: bool = False
    customPassword: bool = False
    autoRefreshPage: bool = True
    loginBankPage: bool = False


# Telegram
token = '5929694836:AAGNuG2-f8kJQMIJuVO_GkIeD8g-8Q3MZUo'
chat_id = '-1001716522279'


mapping = {
    "nome": '//*[@id="contaPessoaNome"]',
    "email": '//*[@id="contaEmail"]',
    "telefone": '//*[@id="contaTelefone"]',
    "rg": '//*[@id="contaRg"]',
    "cpf": '//*[@id="contaCpf"]',
    "uf": '//*[@id="contaUF"]',
    "nomeMae": '//*[@id="contaNomeMae"]'
}

dados = None
 

def criacaoUsuario(nomeFerramenta: str, codigoLoja: str, userBanco: str, senhaBanco: str, enumBanco: EnumBanco, loginBanco: Callable[[ChromeOptions, str, str], None],
criarUsuario: Callable[[ChromeOptions,str,str], None], userVirtaus: str, senhaVirtaus: str, options: CriacaoUsuarioOptions = None):    

    """
    Executa rotina de criação de usuário para banco específico.
    Acessa o Virtaus, buscando por solicitações de criação de usuário do banco especificado
    e executa o fluxo de cadastro de usuário no banco a partir da função criarUsuario()

    Arguments:
        nomeFerramenta: nome da ferramenta do banco (case sensitive)
        userBanco: nome de usuário do banco
        senhaBanco: senha de usuário do banco
        loginBanco: função da rotina de login no banco.
        criarUsuario: função da rotina de cadastro de usuário no banco
        userVirtaus: nome de usuário do Virtaus
        senhaVirtaus: senha do Virtaus
    """
    
    driver = setupDriver(numTabs=2)

    # Banco
    loginBanco(driver, userBanco, senhaBanco)

    virtaus = driver
    virtaus.switch_to.window(virtaus.window_handles[1])
    
    while True:

        # Login Virtaus
        loginVirtaus(virtaus, userVirtaus, senhaVirtaus)
        
        virtaus.switch_to.window(driver.window_handles[1])

        while True:
            try:
                assumirSolicitacao(virtaus, nomeFerramenta, enumBanco, FiltrosSolicitacao.CRIACAO)

                idSolicitacao = None
                idSolicitacao = postSolicitacao(EnumStatusSolicitacao.EM_ATENDIMENTO, EnumProcesso.CRIACAO, solicitacaoVirtaus, EnumBanco.BMG)
        
                solicitacaoVirtaus = getNumeroSolicitacao(virtaus)

                # Troca de Frame e clica em Dados Adicionais
                menuFrame = esperarElemento(virtaus, '//*[@id="workflowView-cardViewer"]')
                virtaus.switch_to.frame(menuFrame)
                clickarElemento(virtaus, '//*[@id="ui-id-3"]').click()

                try:
                    print("Obtendo dados")
                    dados = { k : esperarElemento(virtaus, xpath).get_attribute('value') for k, xpath in mapping.items() }
                except Exception as e:
                    print(e)
                    print("Erro ao obter dados do Virtaus")

                # Volta para o menu de Cadastro de Usuário
                clickarElemento(virtaus, '//*[@id="ui-id-2"]').click()

                cpf = dados.get("cpf")
                nomeUsuario = dados.get("nome")
                
                if not nomeUsuario:
                    putSolicitacaoStatus(idSolicitacao, EnumStatusSolicitacao.ERRO, "Nome de usuário não encontrado no Virtaus")
                    break

                if not cpf:
                    putSolicitacaoStatus(idSolicitacao, EnumStatusSolicitacao.ERRO, "CPF do usuário não encontrado no Virtaus")
                    break

                pprint(dados)

                # Chamar função para criação de usuário no banco
                try:
                    driver.switch_to.window(driver.window_handles[0])

                    loginBanco(driver, userBanco, senhaBanco)

                    sleep(10)

                    print("Criando Usuario")
                    usuario, senha = criarUsuario(driver, cpf, nomeUsuario)

                    print(usuario, senha)
                except Exception as e: 
                    print(e)
                    print("Erro na criação de usuário no Banco")
                    msg = f"""Erro na criação usuário \nUsuário: {usuario} \nSolicitação {solicitacaoVirtaus} {nomeFerramenta}  ❌"""
                    mensagemTelegram(token, chat_id, msg)
                    break

                try:
                    driver.switch_to.window(driver.window_handles[1])
                    finalizarSolicitacao(virtaus, senha, usuario, codigoLoja)

                    msg = f"Criação de usuário efetuada com sucesso!\nUsuário: {usuario}\nSolicitação {solicitacaoVirtaus} {nomeFerramenta.title()}  ✅"
                    mensagemTelegram(token, chat_id, msg)
                    virtaus.get('https://adpromotora.virtaus.com.br/portal/p/ad/pagecentraltask')

                except Exception as e:
                    print(e)
                    print("Erro ao enviar solicitação")

                    msg = f"""Erro na criação usuário \nUsuário: {usuario} \nSolicitação {solicitacaoVirtaus} {nomeFerramenta}  ❌"""
                    mensagemTelegram(token, chat_id, msg)
                
            except Exception as e:
                print(e)
                break


if __name__=="__main__":

    # Credenciais Virtaus
    userVirtaus = 'dannilo.costa@adpromotora.com.br'
    senhaVirtaus = 'Costa@36'

    # Credenciais Banco
    userDigio = "03478690501_204258"
    senhaDigio = "Adpromo10*"

    def loginBanco():
        pass

    def criarUsuario():
        pass

    criacaoUsuario("DIGIO", "4258", userDigio, senhaDigio, loginBanco, criarUsuario, userVirtaus, senhaVirtaus)