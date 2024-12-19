# Controle de Calibração de Equipamentos

Este é um sistema simples de gerenciamento de calibração de equipamentos desenvolvido com Flask e SQLite. Ele permite que os usuários adicionem, visualizem e gerenciem equipamentos, além de monitorar suas datas de calibração e vencimento.

---

## **Funcionalidades**

- Exibição de uma lista de equipamentos cadastrados, com status de calibração (em dia, próximo ao vencimento, vencido).
- Adição de novos equipamentos com informações detalhadas.
- Filtro por localizações específicas.
- Gerenciamento dinâmico de tipos e modelos de equipamentos.
- Endpoint para integrar dados de equipamentos via API.
- Visualização e impressão otimizadas.

---

## **Tecnologias Utilizadas**

- **Backend:** Flask
- **Banco de Dados:** SQLite
- **Frontend:** HTML5, Tailwind CSS
- **Estilização para Impressão:** CSS com `@media print`
- **Template Engine:** Jinja2

---

## **Instalação**

Siga os passos abaixo para executar o projeto em seu ambiente local:

### 1. **Clone o Repositório**

```bash
git clone https://github.com/seuusuario/controle-calibracao.git
cd controle-calibracao
