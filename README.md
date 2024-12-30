# 📄 Regime Apuração

## 📌 Descrição
Este projeto automatiza o envio e processamento de dados relacionados à opção de regime de apuração utilizando a API do SERPRO. Ele processa planilhas Excel, realiza autenticação segura via certificados digitais e salva as respostas em um banco de dados SQLite, além de gerar PDFs das respostas recebidas.

---

## 🚀 Funcionalidades
- 🔍 **Processamento de planilhas Excel** com dados fiscais.
- 🔒 **Autenticação Segura** com certificado digital.
- 📄 **Geração de PDFs** com as respostas da API.
- 📊 **Armazenamento** de respostas no banco de dados SQLite.
- 🔄 **Manipulação de dados** com Pandas para análise e formatação.

---

## 🛠️ Tecnologias Utilizadas
- **Python 3.8 ou superior** – Linguagem principal.
- **Pandas** – Manipulação e análise de dados tabulares.
- **SQLAlchemy** – ORM para gerenciamento de banco de dados.
- **requests-pkcs12** – Requisições HTTPS com autenticação por certificado digital.
- **dotenv** – Gerenciamento de variáveis de ambiente.

---

## 📥 Instalação e Configuração

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/regime-apuracao.git
cd regime-apuracao
```

### 2. Configurar o Ambiente Virtual (Opcional)
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```env
DATABASE_URL=sqlite:///serpro_respostas.db
CAMINHO_CERTIFICADO=/caminho/para/certificado
NOME_CERTIFICADO=certificado.pfx
SENHA_CERTIFICADO=sua_senha
CONSUMER_KEY=sua_consumer_key
CONSUMER_SECRET=sua_consumer_secret
```

### 5. Ajustar Caminho da Planilha
No arquivo `app.py`, ajuste a variável `caminho_planilha` para o arquivo Excel desejado:
```python
caminho_planilha = r'C:\caminho\para\sua\planilha.xlsx'
```

---

## 🧑‍💻 Como Usar

### 1. Processar a Planilha
Execute o script principal para enviar os dados à API do SERPRO:
```bash
python app.py
```

### 2. Resultados
- PDFs gerados estarão na pasta `respostas/`.
- Respostas armazenadas no banco de dados SQLite (`serpro_respostas.db`).

---

## 📂 Estrutura do Projeto

```
Regime_apuracao/
├── .idea/                     # Configurações do IDE (opcional)
├── respostas/                 # Diretório para salvar os PDFs gerados
├── .env                       # Arquivo com variáveis de ambiente
├── app.py                     # Script principal
├── models.py                  # Modelos de banco de dados
├── serpro_auth.py             # Script para autenticação
├── serpro_respostas.db        # Banco de dados SQLite
├── requirements.txt           # Lista de dependências do projeto
```

---

## 🧪 Testes
Testes automatizados podem ser adicionados para verificar a integridade do código. Use `pytest` para rodar os testes (caso configurados):
```bash
pytest tests/
```

---

## ⚠️ Problemas Comuns e Soluções

### **1. Erro: "Arquivo Excel não encontrado"**
Certifique-se de que o caminho especificado em `caminho_planilha` está correto.

### **2. Erro de Autenticação na API do SERPRO**
- Verifique se as credenciais no `.env` estão corretas.
- Confirme se o certificado digital está no caminho especificado.

### **3. Erro ao Salvar PDF**
Certifique-se de que a pasta `respostas/` existe ou que o script tem permissão para criar pastas.

---



