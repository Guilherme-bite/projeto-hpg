# ConferePix - Pagamentos HPG

**Aluno:** Guilherme Claudino dos Santos de Sa
**Curso:** CST em Análise e Desenvolvimento de Sistemas
**Disciplina:** Projeto de Software - Experiência Prática

---

## 📌 Sobre o Projeto
O **ConferePix** é um Produto Mínimo Viável (MVP) de uma aplicação web responsiva desenvolvida para solucionar um problema real da **HPG Comércio S.A.**, uma loja de varejo localizada em São Paulo que atua na venda de celulares e acessórios.

O projeto foi construído ao longo das Experiências Práticas 1 e 2, conectando o diagnóstico comunitário à criação de uma solução tecnológica alinhada ao **ODS 8 (Trabalho Decente e Crescimento Econômico)** da ONU.

## 🎯 O Problema Real
A HPG recebe cerca de 40 pedidos por dia, e um único pedido pode ser pago com até 3 Pix diferentes. Atualmente, os comprovantes ficam espalhados entre a galeria do celular e o WhatsApp, enquanto os pagamentos em dinheiro e a fornecedores são anotados em papel. 

A conferência é feita manualmente a cada 7 dias, levando de 2 a 4 horas, o que gera retrabalho, risco de divergências e impede o acompanhamento diário do caixa. O MVP atua diretamente na **centralização dessas informações**.

## 💡 A Solução (Escopo do MVP)
O sistema foi desenhado para ser simples, rápido e focado no uso pelo celular no balcão da loja. Suas principais funcionalidades são:
1. **Cadastro de Pedidos:** Registro do número do pedido, cliente e valor total.
2. **Múltiplos Pagamentos:** Associação de um ou mais pagamentos (Pix ou Dinheiro) ao mesmo pedido, com upload obrigatório de comprovante para Pix.
3. **Cálculo Automático de Situação:** O sistema calcula sozinho se o pedido está *Pendente*, *Parcial*, *Pago* ou *A Conferir* (caso o valor pago seja maior que o total).
4. **Conferência Diária:** Painel que substitui a conferência semanal, mostrando os totais recebidos por método de pagamento no dia.

## 🏗️ Arquitetura e Tecnologias
O projeto foi desenvolvido utilizando as melhores práticas de desenvolvimento web e uma arquitetura em camadas (Service Layer) para separar responsabilidades:
*   **Backend:** Python com Flask (Blueprints para modularização).
*   **Banco de Dados:** SQLite com SQLAlchemy (ORM).
*   **Frontend:** HTML5, Jinja2 (Templates), CSS3 customizado (Mobile-first).
*   **Testes:** Pytest (54 testes automatizados cobrindo regras de negócio, autenticação e integridade).
*   **Segurança:** Hash de senha com Scrypt, proteção CSRF, bloqueio após 5 tentativas de login e sanitização de uploads de arquivos.

## 🔒 Segurança e Qualidade (Auto-Revisão)
*   **Refatoração (Service Layer):** As regras de negócio (cálculo de situação) estão isoladas em `app/services/`, não sobrecarregando as rotas.
*   **Integridade no Banco:** Uso de `CheckConstraints` para impedir valores negativos e garantir que todo Pix tenha comprovante.
*   **Tratamento de Exceções:** Rotas preparam `try/except` para evitar que erros de banco de dados quebrem a aplicação, retornando mensagens amigáveis ao usuário.

## 🚀 Como Executar o Projeto Localmente

### 1. Pré-requisitos
*   Python 3.10+
*   Git

### 2. Passo a passo
```bash
# Clone o repositório
git clone https://github.com/Guilherme-bite/projeto-hpg.git
cd projeto-hpg

# Crie e ative o ambiente virtual
python -m venv .venv
# No Windows:
.venv\Scripts\activate
# No Linux/Mac:
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Crie o arquivo .env com base no .env.example e defina sua SECRET_KEY
# Inicialize o banco de dados
python init_db.py

# Crie um usuário de teste (será solicitado login e senha)
python criar_usuario.py

# Rode a aplicação
python run.py
