from abc import ABC, abstractmethod
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__ (self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    
    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("Saldo insuficiente.")

        elif valor > 0:
            self._saldo -= valor
            print("Saque realizado com sucesso.")
            return True
        else:
            print("Não foi possível realizar o saque.")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("Depósito realizado com sucesso.")
        else:
            return False
        
        return True
    
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques
        self._saques = 0

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao['tipo'] == Saque.__name__])

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("O valor do saque excede o limite.")

        elif excedeu_saques:
            print("Número de saques excedido.")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f'CC: {self._agencia}/{self._numero} - {self._cliente.nome}'
    
class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                'data': datetime.now().strftime('%d-%m-%Y %H:%M:%s'),
                'tipo': transacao.__class__.__name__,
                'valor': transacao.valor
            }
    )

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso = conta.sacar(self._valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        conta.depositar(self._valor)


def menu():
    clientes =[]
    contas = []

    while True:
        opcao = menu()

        if opcao == '1':
            depositar(clientes)

        elif opcao == '2':
            sacar(clientes)

        elif opcao == '3':
            exibir_extrato(clientes)
        
        elif opcao == '4':
            criar_cliente(clientes)

        elif opcao == '5':
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, contas, clientes)

        elif opcao == '6':
            listar_contas(contas)

        elif opcao == '7':
            break

        else:
            print("Opção inválida, por favor tente novamente.")

def filtrar_clientes(cpf, clientes):
    clientes_filtrado = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrado[0] if len(clientes_filtrado) == 1 else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        return None
    else:
        return cliente.contas[0]
    
def depositar(clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print("CPF não encontrado.")
        return

    valor = float(input("Digite o valor a ser depositado: "))
    cliente.realizar_transacao(cliente.contas[0], Deposito(valor))

    if not cliente:
        print("cliente não encontrado.")
        return
    
    valor = float(input("Digite o valor a ser depositado: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)

    transacao.registrar(conta)
    cliente.contas.append(conta)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print("CPF não encontrado.")
        return
    
    valor = float(input("Digite o valor a ser sacado: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return
    
def exibir_extrato(clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print("CPF não encontrado.")
        return
    
    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return
    
    print("Extrato:")
    transacoes = conta.historico.transacao

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['data']} - {transacao['tipo']} - {transacao['valor']}"

    print(f"\n{extrato}")
    print(f"\nSaldo: {conta.saldo:.2f}")

def criar_conta(numero_conta, contas, clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print("CPF não encontrado.")
        return
    
    conta = ContaCorrente.nova_conta(cliente, numero_conta)
    contas.append(conta)
    print("Conta criada com sucesso.")

def criar_cliente(clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if cliente:
        print("CPF já existente.")
        return
    
    nome = input("Digite o nome do cliente: ")
    data_nascimento = input("Digite a data de nascimento do cliente: ")
    cliente = PessoaFisica(nome, data_nascimento, cpf)
    clientes.append(cliente)
    print("Cliente criado com sucesso.")

def listar_contas(contas):
    for conta in contas:
        print(f"Agência: {conta.agencia} | Número da conta: {conta.numero}")





menu()