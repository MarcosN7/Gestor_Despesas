# Gestor de Despesas Pessoal

![Versão](https://img.shields.io/badge/versão-3.1-blue)
![Python](https://img.shields.io/badge/Python-3.9+-brightgreen)
![Licença](https://img.shields.io/badge/Licença-MIT-lightgrey)

Um aplicação de desktop moderna e intuitiva para gestão e visualização de despesas pessoais, construída em Python com a biblioteca CustomTkinter.

## Descrição

Este projeto foi criado para ajudar no controlo de finanças pessoais. Ele permite que o utilizador adicione despesas mensais, categorize-as e visualize os seus padrões de gastos através de uma interface limpa e de relatórios detalhados, incluindo gráficos interativos e exportação para PDF.

## Funcionalidades Principais

- **Adicionar Despesas:** Registe despesas com informações detalhadas como ano, mês, categoria, valor e tipo de moeda (BRL, USD, EUR).
- **Visualização em Tabela:** Todas as despesas são exibidas numa tabela clara e organizada.
- **Filtros Dinâmicos:** Filtre facilmente as suas despesas por moeda, ano, mês ou categoria para análises específicas.
- **Cálculos Automáticos:** Veja o total gasto para a seleção atual de filtros.
- **Gráficos Interativos:** Gere gráficos de barras e pizza com a biblioteca Plotly para entender melhor a distribuição dos seus gastos. Os gráficos abrem no navegador para total interatividade.
- **Relatórios em PDF:** Exporte um resumo profissional da sua vista atual para um ficheiro PDF, incluindo gráficos de barras, pizza e um gráfico de evolução temporal.
- **Exportação para CSV:** Exporte todos os seus dados para um ficheiro CSV para poder usá-los em outras ferramentas como Excel ou Google Sheets.
- **Persistência de Dados:** Os dados são guardados numa base de dados SQLite (`expenses.db`), garantindo que as suas informações estejam sempre disponíveis.
- **Seguro e Privado:** O código não contém informações sigilosas e o ficheiro da base de dados pessoal é ignorado pelo Git através do `.gitignore`.

## Screenshots

![Screenshot da Aplicação Principal](/images/00001.jpg)

## Tecnologias Utilizadas

- **Python 3**
- **CustomTkinter:** Para a interface gráfica moderna.
- **Pandas:** Para manipulação e análise de dados.
- **Plotly:** Para a criação de gráficos interativos.
- **ReportLab:** Para a geração de relatórios em PDF.
- **SQLite3:** Para a base de dados local.

## Como Executar o Projeto

Siga os passos abaixo para executar o projeto no seu computador.

### Pré-requisitos

- Python 3.8 ou superior
- `pip` (gestor de pacotes do Python)

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/gestor-de-despesas-python.git](https://github.com/seu-usuario/gestor-de-despesas-python.git)
    cd gestor-de-despesas-python
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    Este projeto usa um ficheiro `requirements.txt` para gerir as dependências. Execute o seguinte comando:
    ```bash
    pip install -r requirements.txt
    ```

### Execução

Para iniciar a aplicação, basta executar o script principal:
```bash
python gestor_despesas.py
```

## Como Utilizar

1.  **Adicionar uma Despesa:** Preencha os campos no painel esquerdo (Moeda, Ano, Mês, Categoria, Valor) e clique em "Adicionar Despesa".
2.  **Filtrar Despesas:** Use os menus dropdown no topo do painel direito e clique em "Aplicar" para filtrar a tabela. Clique em "Limpar" para remover todos os filtros.
3.  **Gerar Gráficos:** Com os dados filtrados (ou não), clique em "Gráficos Padrão" para abrir visualizações interativas no seu navegador.
4.  **Exportar para PDF:** Clique em "Exportar Resumo p/ PDF" para gerar um relatório da vista atual. Lembre-se que esta funcionalidade requer que os dados na vista sejam de uma única moeda.
5.  **Apagar uma Despesa:** Clique numa ou mais despesas na tabela (use Ctrl+Click para selecionar várias) e clique no botão "Apagar Despesa Selecionada".

---
