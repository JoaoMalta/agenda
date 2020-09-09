import os
import sys
from typing import List
from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt


if sys.platform.lower() == 'win32':
    os.system('color')  # permite o reconhecimento dos codigos ANSI pelo terminal do windows.


TODO_FILE = 'todo.txt'
ARCHIVE_FILE = 'done.txt'

RED = "\033[0;31m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[1m"
REVERSE = "\033[;7m"
YELLOW = "\033[0;33m"

ADICIONAR = 'a'
REMOVER = 'r'
FAZER = 'f'
PRIORIZAR = 'p'
LISTAR = 'l'
DESENHAR = 'g'


# Cria uma nova classe para representar os compromissos.
class Compromisso:
    def __init__(self, data: str, hora: str, pri: str, desc: str, contexto: str, projeto: str):
        self.data = data
        self.hora = hora
        self.prioridade = pri
        self.descricao = desc
        self.contexto = contexto
        self.projeto = projeto
        return

    def novaAtividade(self):
        atividade = ''
        if self.data != '':
            atividade += self.data + ' '
        if self.hora != '':
            atividade += self.hora + ' '
        if self.prioridade != '':
            atividade += self.prioridade + ' '
        atividade += self.descricao
        if self.contexto != '':
            atividade += ' ' + self.contexto
        if self.projeto != '':
            atividade += ' ' + self.projeto
        return atividade


# Imprime texto com cores.
def printCores(texto, cor):
    print(cor + texto + RESET)


def adicionar(compromisso: Compromisso, arquivo: str) -> bool:
    # não é possível adicionar uma atividade que não possui descrição.
    if compromisso.descricao == '':
        return False
    # Escreve no arquivo (TODO_FILE ou ARCHIVE_FIVE).
    try:
        fp = open(arquivo, 'a')
        fp.write(compromisso.novaAtividade() + "\n")
    except IOError as err:
        print("Não foi possível escrever para o arquivo " + arquivo)
        print(err)
        return False
    finally:
        fp.close()

    return True


# Valida a prioridade.
def prioridadeValida(pri: str) -> bool:
    if len(pri) == 3:
        if pri[0] == '(' and pri[2] == ')':
            if pri[1].lower() >= 'a' and pri[1].lower() <= 'z':
                return True
    return False


# Valida a hora. Consideramos que o dia tem 24 horas, como no Brasil, ao invés
# de dois blocos de 12 (AM e PM), como nos EUA.
def horaValida(horaMin: str) -> bool:
    if len(horaMin) != 4 or not soDigitos(horaMin):
        return False
    else:
        hora = int(horaMin[0:2])
        min = int(horaMin[2:4])
        if hora < 0 or hora > 23 or min < 0 or min > 59:
            return False
        return True


# Valida datas. Verificar inclusive se não estamos tentando
# colocar 31 dias em fevereiro. Não precisamos nos certificar, porém,
# de que um ano é bissexto.
def dataValida(data: str) -> bool:
    if len(data) == 8 and soDigitos(data):
        dia = int(data[0:2])
        mes = int(data[2:4])
        ano = int(data[4:8])
        if ano > 0 and mes >= 1 and mes <= 12 and dia >= 1:
            if mes in [1, 3, 5, 7, 8, 10, 12] and dia <= 31:
                return True
            elif mes == 2 and dia <= 29:
                return True
            elif mes in [4, 6, 9, 11] and dia <= 30:
                return True
    return False


# Valida que o string do projeto está no formato correto.
def projetoValido(proj: str) -> bool:
    if len(proj) >= 2 and proj[0] == '+':
        return True
    else:
        return False


# Valida que o string do contexto está no formato correto.
def contextoValido(cont: str) -> bool:
    if len(cont) >= 2 and cont[0] == '@':
        return True
    else:
        return False


# Valida que a data ou a hora contém apenas dígitos, desprezando espaços
# extras no início e no fim.
def soDigitos(numero: str) -> bool:
    if type(numero) != str:
        return False
    for x in numero:
        if x < '0' or x > '9':
            return False
    return True


# Todos os itens menos DESC são opcionais. Se qualquer um deles estiver fora do formato, por exemplo,
# data que não tem todos os componentes ou prioridade com mais de um caractere (além dos parênteses),
# tudo que vier depois será considerado parte da descrição.
def organizar(linhas: List[str]) -> List[Compromisso]:
    itens = []

    for l in linhas:
        data = ''
        hora = ''
        pri = ''
        contexto = ''
        projeto = ''

        l = l.strip()  # remove espaços em branco e quebras de linha do começo e do fim
        tokens = l.split()  # quebra o string em palavras

        try:
            if dataValida(tokens[0]):
                data = tokens.pop(0)
            if horaValida(tokens[0]):
                hora = tokens.pop(0)
            if prioridadeValida(tokens[0]):
                pri = tokens.pop(0)
            if projetoValido(tokens[-1]):
                projeto = tokens.pop()
            if contextoValido(tokens[-1]):
                contexto = tokens.pop()
        except IndexError:
            print('Atividade inválida. Uma atividade deve conter um descrição.')
            exit()
        else:
            if ' '.join(tokens) != '':
                desc = ' '.join(tokens)
                itens.append(Compromisso(data, hora, pri, desc, contexto, projeto))
            else:
                print('Atividade inválida. Uma atividade deve conter um descrição.')
                exit()
    return itens


# A função listar() organiza e exibe os compromissos do arquivo TODO_FILE segundo suas prioridades, data e hora
def listar() -> bool:
    try:
        fp = open(TODO_FILE, 'r')
    except IOError as err:
        print("Não foi possível ler o arquivo " + TODO_FILE)
        print(err)
        return False
    else:
        ls: List[str] = list(fp)  # Carrega as informações do arquivo TODO_FILE em uma lista de strings
        listaObjetos: List[Compromisso] = organizar(ls)  # Transforma a lista de Str em uma lista de Compromisso
        listaOrdenada: List[Compromisso] = listaObjetos[:]  # cria uma copia da lista de objetos para ser ordenada
        listaOrdenada = ordenarPorDataHora(listaOrdenada)  # ordena as atividades por data e hora
        listaOrdenada = ordenarPorPrioridade(listaOrdenada)  # Ordena as atividades por prioridade
        # imprime os compromissos com formatação em cores
        for l in listaOrdenada:
            texto = str(listaObjetos.index(l)+1) + " " + l.novaAtividade()
            if l.prioridade == '(A)':
                printCores(texto, RED+BOLD)
            elif l.prioridade == '(B)':
                printCores(texto, YELLOW)
            elif l.prioridade == '(C)':
                printCores(texto, CYAN)
            elif l.prioridade == '(D)':
                printCores(texto, GREEN)
            else:
                print(listaObjetos.index(l)+1, l.novaAtividade())
        fp.close()
    return True


# Trata as datas (string) dos comrpomisso para um formato (date) para que facilite a comparação.
def dataComparavel(compromisso: Compromisso) -> datetime.date:
    if compromisso.data != '':
        dia = int(compromisso.data[0:2])
        mes = int(compromisso.data[2:4])
        ano = int(compromisso.data[4:8])
        return date(ano, mes, dia)
    else:
        return date(2200, 12, 30)


# Trata a hora dos compromissos para facilitar a ordenação das atividades.
def horaComparavel(compromisso: Compromisso) -> str:
    if compromisso.hora != '':
        return compromisso.hora
    else:
        return "9999"


# Ordena os compromissos por hora e por data. As mais antigas aparecem primeiro.
def ordenarPorDataHora(itens: List[Compromisso]) -> List[Compromisso]:
    itens.sort(key=horaComparavel)
    itens.sort(key=dataComparavel)
    return itens


# Ordena os compromissos por prioridade. Prioridade mais alta aparece primeiro.
def ordenarPorPrioridade(itens: List[Compromisso]) -> List[Compromisso]:

    comPrioridade: List[Compromisso] = [x for x in itens if x.prioridade != ""]
    semPrioridade: List[Compromisso] = [y for y in itens if y.prioridade == ""]
    comPrioridade = sorted(comPrioridade, key=lambda compromisso: compromisso.prioridade)
    itens = comPrioridade + semPrioridade
    return itens


# A função fazer() remove uma compromisso concluido do arquivo TODO_FILE e adiciona-o ao arquivo ARCHIVE_FILE.
def fazer(num: int) -> bool:
    try:
        f = open(TODO_FILE, 'r')
    except IOError as err:
        print("Não foi possível ler o arquivo " + TODO_FILE)
        print(err)
        return False
    else:
        ls: List[str] = list(f)
        itemFeito: Compromisso = organizar([ls[num - 1]])[0]
        adicionar(itemFeito, ARCHIVE_FILE)
        f.close()
        remover(num)
        return True


# A função Remover() retira um compromisso do arquivo TODO_FILE.
def remover(numero: int) -> bool:
    try:
        f = open(TODO_FILE, "r")
        ls: List[str] = list(f)
    except IOError as err:
        print("Não foi possível acessar o arquivo " + TODO_FILE)
        print(err)
        return False
    else:
        f.close()
        try:
            ls.pop(numero - 1)
        except IndexError:
            print(f'Número da atividade inválido. Escolha uma atividade entre 1 e {len(ls)}.')
            return False
        else:
            try:
                f = open(TODO_FILE, 'w')
                for i in range(0, len(ls)):
                    f.write(ls[i])
            except IOError as err:
                print("Não foi possível escrever para o arquivo " + TODO_FILE)
                print(err)
                return False
            finally:
                f.close()
    finally:
        f.close()
        return True


# Modifica a prioridade de um determinado Compromisso.
def priorizar(num: int, prioridade: str) -> bool:
    try:
        f = open(TODO_FILE, "r")
    except IOError as err:
        print("Não foi possível acessar o arquivo " + TODO_FILE)
        print(err)
        return False
    else:
        ls: List[str] = list(f)
        f.close()
        try:
            itemParaPriorizar: Compromisso = organizar([ls[num - 1]])[0]
            itemParaPriorizar.prioridade = '(' + prioridade.upper() + ')'
            ls[num - 1] = itemParaPriorizar.novaAtividade() + '\n'
        except IndexError:
            print(f'Número da atividade inválido. Escolha uma atividade entre 1 e {len(ls)}.')
            return False
        else:
            itemParaPriorizar.prioridade = '(' + prioridade.upper() + ')'
            ls[num - 1] = itemParaPriorizar.novaAtividade() + '\n'
            try:
                f = open(TODO_FILE, 'w')
                for i in range(0, len(ls)):
                    f.write(ls[i])
            except IOError as err:
                print("Não foi possível escrever para o arquivo " + TODO_FILE)
                print(err)
                return False
            finally:
                f.close()
    finally:
        f.close()
        return True


def desenhar(dias: int) -> bool:
    x = []
    for i in range(dias, 0, -1):
        xi = datetime.now() - timedelta(days=i)
        x.append(xi.strftime('%d/%m/%y'))
    try:
        f = open(ARCHIVE_FILE, 'r')
    except IOError as err:
        print("Não foi possível ler o arquivo " + TODO_FILE)
        print(err)
        return False
    else:
        ls: List[str] = list(f)
        lo: List[Compromisso] = organizar(ls)
        y = []
        for i in x:
            aux: int = 0
            for l in lo:
                if dataComparavel(l).strftime('%d/%m/%y') == i:
                    aux += 1
            y.append(aux)
        plt.plot(x, y)
        plt.show()
    return True


# A Função processarComandos é a função principal que chama as demais funções.
def processarComandos(comandos: List[str]):
    if comandos[1] == ADICIONAR:
        comandos.pop(0)  # remove 'agenda.py'
        comandos.pop(0)  # remove 'adicionar'
        itemParaAdicionar: Compromisso = organizar([' '.join(comandos)])[0]
        adicionar(itemParaAdicionar, TODO_FILE)  # novos itens não têm prioridade
        return
    elif comandos[1] == LISTAR:
        listar()
        return
    elif comandos[1] == REMOVER:
        if comandos[2].isnumeric():
            remover(int(comandos[2]))
        else:
            print('Digite um número de atividade válido.')
        return

    elif comandos[1] == FAZER:
        if comandos[2].isnumeric():
            fazer(int(comandos[2]))
        else:
            print('Digite um número de atividade válido.')
        return
    elif comandos[1] == PRIORIZAR:
        if comandos[2].isnumeric():
            if comandos[3].isalpha():
                priorizar(int(comandos[2]), comandos[3])
            else:
                print('Digite uma prioridade válida.')
        else:
            print('Digite um número de atividade válido.')
        return
    elif comandos[1] == DESENHAR:
        if comandos[2].isnumeric():
            desenhar(int(comandos[2]))
        else:
            print('Digite um número válido.')
        return
    else:
        print("Comando inválido.")


processarComandos(sys.argv)
