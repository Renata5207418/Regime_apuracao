from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

"""
Base: A classe base que todas as classes de modelo (como Requisicao) herdarão. Isso é necessário para o SQLAlchemy 
identificar as classes que devem ser mapeadas para as tabelas do banco de dados.
"""
Base = declarative_base()


class Requisicao(Base):
    __tablename__ = 'requisicoes'

    id = Column(Integer, primary_key=True)
    cnpj_matriz = Column(String(14), nullable=False)
    ano_calendario = Column(Integer, nullable=False)
    regime_escolhido = Column(String, nullable=False)
    data_hora_opcao = Column(String(14), nullable=False)
    demonstrativo_pdf_base64 = Column(String, nullable=True)

    def __repr__(self):
        """
        __repr__: Método especial que define a representação legível de uma instância da classe. Ele é útil para
         depuração, pois permite ver uma descrição concisa da instância.
         A representação inclui o cnpj_matriz, ano_calendario e regime_escolhido, que são os campos mais
         importantes para identificação da requisição.
        """
        return (f"<Requisicao(cnpj_matriz={self.cnpj_matriz}, ano_calendario={self.ano_calendario}, "
                f"regime_escolhido={self.regime_escolhido})>")
