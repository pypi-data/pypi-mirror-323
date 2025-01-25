import requests
from enum import Enum
from requests.exceptions import RequestException, Timeout, ConnectionError


class EnumStatusAcompanhamento(Enum):
    VAZIO = 0
    ERRO = 1
    LIGADO = 2
    DESLIGADO = 3
    IMPORTANDO = 4
    APROVADO = 5
    CANCELADA = 6
    SEM_ARQUIVOS = 8


class EnumStatus(Enum):
    VAZIO = 0
    ERRO = 1
    LIGADO = 2
    DESLIGADO = 3
    IMPORTANDO = 4
    APROVADO = 5
    CANCELADA = 6
    SEM_PROPOSTA = 7
    SEM_ARQUIVOS = 8


class EnumProcesso(Enum):
    INTEGRACAO = 0
    IMPORTACAO = 1
    APROVADORES = 2
    BLIP_CONSULTA = 3
    BLIP_LINK = 4
    PAG_DEV = 5
    JURIDICO = 6
    RESET = 10
    COLETAR_DOCUMENTO = 8
    CRIACAO = 9
    CONFIRMACAO_CREDITO = 11


class EnumBanco(Enum):
    VAZIO = 0
    PAN = 1
    OLE = 2
    MEU_CASH_CARD = 3
    BMG = 4
    DIGIO = 5
    BRADESCO = 5
    BANRISUL = 6
    BANCO_DO_BRASIL = 7
    C6 = 8
    ITAU = 9
    MASTER = 10
    PAULISTA = 11
    CREFAZ = 12
    CCB = 13
    DAYCOVAL = 14
    ICRED = 15
    HAPPY_AMIGOZ = 16
    SAFRA = 17
    SANTANDER = 18
    VIRTAUS = 19
    CREFISA = 20
    FACTA = 21
    JBCRED = 22
    FUTURO_PREVIDENCIA = 23
    CREFISA_CP = 24
    PAN_CARTAO = 25
    PAN_PORT = 26
    HAPPY_PORT = 27
    NUVIDEO = 28
    PROMOBANK = 29
    BLIP = 30
    GETDOC = 31
    DAYCOVAL_CARTAO = 32


class EnumStatusSolicitacao(Enum):
    EM_ATENDIMENTO = 0
    CONCLUIDO = 1
    ERRO = 2
    TRANSFERIDO = 3


class IdSolicitacaoCriacaoBanco(Enum):
    BMG = 41
    C6 = 42
    DIGIO = 47
    BRADESCO = 47
    ITAU = 44
    VIRTAUS = 46

    @classmethod
    def getEnum(cls, key):
        try:
            return cls[key].value
        except KeyError:
            raise ValueError(f"Chave {key} não encontrada em {cls.__name__}.")


class IdSolicitacaoResetBanco(Enum):
    BMG = 15
    MASTER = 17
    CREDCESTA = 17
    ITAU = 19
    BANRISUL = 20
    FACTA = 21
    CREFISA = 22
    DIGIO = 38
    BRADESCO = 38

    @classmethod
    def getEnum(cls, key):
        try:
            return cls[key].value
        except KeyError:
            raise ValueError(f"Chave {key} não encontrada em {cls.__name__}.")



def putStatusRobo(status: EnumStatus, enumProcesso: EnumProcesso, enumBanco: EnumBanco):
    """
    Envia duas requisições HTTP PUT para atualizar o status de um processo e registrar o horário da atualização.

    Parâmetros:
    ----------
    status : IntegracaoStatus
        Um valor da enumeração `IntegracaoStatus` que representa o status do processo a ser atualizado.
    enumProcesso : int
        Um número inteiro que representa o ID do processo a ser atualizado.
    enumBanco : int
        Um número inteiro que representa o ID do banco a ser atualizado.
    """
    PORTA = 7118
    
    if enumProcesso in [EnumProcesso.INTEGRACAO, EnumProcesso.IMPORTACAO]:
        PORTA = 8443

    horaFeita = f'http://172.16.10.6:{PORTA}/acompanhamentoTotal/horaFeita/{enumProcesso.value}/{enumBanco.value}'
    URLnovaApi = f'http://172.16.10.6:{PORTA}/acompanhamentoTotal/processoAndBancoStatus/{enumProcesso.value}/{enumBanco.value}'

    data = { "status": status.value }
    headers = { "Content-Type": "application/json" }
    try:
        response = requests.put(URLnovaApi, headers=headers, json=data)

    except requests.Timeout:
        print("A requisição expirou. Verifique sua conexão ou o servidor.")
    except ConnectionError:
        print("Erro de conexão. Verifique sua rede ou o servidor.")
    except requests.RequestException as e:
        print(f"Ocorreu um erro ao realizar a requisição: {e}")

    if status != EnumStatus.DESLIGADO:
        requests.put(horaFeita)

    if response.status_code == 200: 
        pass
        # print("Requisição PUT bem-sucedida!")
        # print("Resposta:", response.json())
    else:
        print(f"Falha na requisição PUT. Código de status: {response.status_code}")
        # print("Resposta:", response.text)


def putSolicitacaoStatus(idSolicitacao: int, enumStatus: EnumStatusSolicitacao, observacao: str = ""):
    data = {
        "enumDetalheSolicitacoesStatus": enumStatus.value,
        "observação": observacao
    }
    headers = {
        "Content-Type": "application/json"
    }

    URLChangeStatus = f'http://172.16.10.6:7118/detalhesSolicitacao/{idSolicitacao}'

    try:
        response = requests.put(URLChangeStatus, headers=headers, json=data)

        if response.status_code == 200:
            # print("Requisição PUT bem-sucedida!")
            requests.put(f'http://172.16.10.6:7118/detalhesSolicitacao/horaFim/{idSolicitacao}', headers=headers, json=data)
        else:
            print(f"Falha na requisição PUT. Código de status: {response.status_code}")
            print("Resposta:", response.text)
    except Timeout:
        print("A requisição expirou. Verifique sua conexão ou o servidor.")
    except ConnectionError:
        print("Erro de conexão. Verifique sua rede ou o servidor.")
    except RequestException as e:
        print(f"Ocorreu um erro ao realizar a requisição: {e}")


def postSolicitacao(enumStatusSolicitacao: EnumStatusSolicitacao, enumProcesso: EnumProcesso, solicitacao: int, enumBanco: EnumBanco) -> int:
    
    mapping =   {
                    EnumProcesso.CRIACAO : IdSolicitacaoCriacaoBanco,
                    EnumProcesso.RESET: IdSolicitacaoResetBanco
                }
    
    idBanco = mapping[enumProcesso].getEnum(enumBanco.name)
    
    data = {
        "enumDetalheSolicitacoesStatus": enumStatusSolicitacao.value,
        "numeroSolicitacao": solicitacao,
        "acompanhamentoDomain": {
            "acompanhamentoId": idBanco
        }
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post("http://172.16.10.6:7118/detalhesSolicitacao/", headers=headers, json=data)

    if response.status_code == 200:
        pass
        # print("Requisição POST bem-sucedida!")
        # print("Resposta:", response.json()) 
    
    else:
        print(f"Falha na requisição POST. Código de status: {response.status_code}")
        # print("Resposta:", response.text)

    dataApi = response.json()
    print(dataApi)
    detalhesSolicitacaoId = dataApi['detalhesSolicitacaoId']

    return detalhesSolicitacaoId


def putTicket(solicitacao: str, enumProcesso: EnumProcesso, enumBanco: EnumBanco):
    data = {
        "solicitacao": solicitacao
    }
    headers = {
        "Content-Type": "application/json"
    }

    URLChangeStatus = f'http://172.16.10.6:8443/acompanhamentoTotal/processoAndBancoSolicitacao/{enumProcesso.value}/{enumBanco.value}'

    try:
        response = requests.put(URLChangeStatus, headers=headers, json=data)

        if response.status_code == 200:
            # print("Requisição PUT bem-sucedida!")
            pass
        else:
            print(f"Falha na requisição PUT. Código de status: {response.status_code}")
            print("Resposta:", response.text)
    except Timeout:
        print("A requisição expirou. Verifique sua conexão ou o servidor.")
    except ConnectionError:
        print("Erro de conexão. Verifique sua rede ou o servidor.")
    except RequestException as e:
        print(f"Ocorreu um erro ao realizar a requisição: {e}")


if __name__=="__main__":
    # putStatusRobo(EnumStatus.LIGADO, EnumProcesso.RESET, EnumBanco.DIGIO)
    #putStatusRobo(EnumStatus.LIGADO, EnumProcesso.CRIACAO, EnumBanco.BMG)
    putStatusRobo(EnumStatus.DESLIGADO, EnumProcesso.IMPORTACAO, EnumBanco.DAYCOVAL_CARTAO)
    # postSolicitacao(None, EnumProcesso.CRIACAO, 123345, EnumBanco.BANRISUL)
    # putStatusRobo(EnumStatus.LIGADO, EnumProcesso.IMPORTACAO, EnumBanco.MEU_CASH_CARD)
    # putStatusRobo(EnumStatus.LIGADO, EnumProcesso.RESET, EnumBanco.BANRISUL)
    #postSolicitacao(EnumStatusSolicitacao.EM_ATENDIMENTO, EnumProcesso.RESET, 123456, EnumBanco.DIGIO)
    pass