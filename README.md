# Coleta de Dados do IBGE

Este desafio da QCA sobre coleta dados dos estados brasileiros no site do IBGE usando Playwright em Python e salva num arquivo JSON.

## Como funciona

* O script abre o site do IBGE e busca pelo estado.
* Navega até a página do estado e coleta informações agrupadas por categorias (ex: População, Educação).
* Armazena os dados organizados em um arquivo `dados_estados.json`.
* Roda tudo em modo headless (sem abrir navegador na tela).

## Ambiente e configuração

* Tenha Python 3.8+ instalado.
* Crie e ative um ambiente virtual no terminal:

    ```bash
    python -m venv env
    ```

* No Windows:

    ```bash
    .\env\Scripts\activate
    ```

* No Linux/macOS:

    ```bash
    source env/bin/activate
    ```

* Instale as dependências:

    ```bash
    pip install playwright
    python -m playwright install
    ```

* (Opcional) Crie um arquivo `.env` para configurar se quer rodar headless (exemplo: `HEADLESS=true`).
* Execute o script:

    ```bash
    python seu_script.py
    ```
