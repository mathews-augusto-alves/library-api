"""
Exceções personalizadas para o domínio da aplicação
"""

class DomainException(Exception):
	"""Exceção base para o domínio"""
	pass

class EmailJaExisteException(DomainException):
	"""Exceção lançada quando o email já existe"""
	def __init__(self, email: str):
		self.email = email
		super().__init__(f"Email '{email}' já está cadastrado")

class PessoaNaoEncontradaException(DomainException):
	"""Exceção lançada quando a pessoa não é encontrada"""
	def __init__(self, pessoa_id: int):
		self.pessoa_id = pessoa_id
		super().__init__(f"Pessoa com ID {pessoa_id} não encontrada")

class DadosInvalidosException(DomainException):
	"""Exceção lançada quando os dados são inválidos"""
	def __init__(self, campo: str, valor: str):
		self.campo = campo
		self.valor = valor
		super().__init__(f"Campo '{campo}' com valor '{valor}' é inválido")

class LivroNaoEncontradoException(DomainException):
	def __init__(self, livro_id: int):
		self.livro_id = livro_id
		super().__init__(f"Livro com ID {livro_id} não encontrado")

class LivroIndisponivelException(DomainException):
	def __init__(self, livro_id: int):
		self.livro_id = livro_id
		super().__init__(f"Livro com ID {livro_id} está indisponível para empréstimo")

class EmprestimoAtivoNaoEncontradoException(DomainException):
	def __init__(self, livro_id: int):
		self.livro_id = livro_id
		super().__init__(f"Não há empréstimo ativo para o livro ID {livro_id}") 