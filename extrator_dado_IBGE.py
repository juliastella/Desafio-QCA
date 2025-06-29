from playwright.sync_api import sync_playwright
import json
import re

def clean_title_simple(title):
    title = title.replace('\n', ' ').strip()
    title = re.sub(r'\s+', ' ', title)
    return title

def extrair_dados_da_pagina(page):
    page.wait_for_selector('.lista__nome')

    population_data = {}

    rows = page.query_selector_all('tr')

    for row in rows:
        name_cell = row.query_selector('td.lista__nome')
        value_cell = row.query_selector('td.lista__valor')

        if name_cell and value_cell:
            raw_title = name_cell.inner_text()
            title = clean_title_simple(raw_title)

            value_span = value_cell.query_selector('span:not(.unidade)')
            value = value_span.inner_text().strip() if value_span else "N/A"

            unit_span = value_cell.query_selector('span.unidade')
            unit = unit_span.inner_text().strip() if unit_span else ""

            full_value = f"{value} {unit}".strip()

            population_data[title] = full_value

    return population_data

# Mapeamento correto das siglas para os estados brasileiros
estados = {
    "Acre": "ac", "Alagoas": "al", "Amapá": "ap", "Amazonas": "am",
    "Bahia": "ba", "Ceará": "ce", "Distrito Federal": "df", "Espírito Santo": "es",
    "Goiás": "go", "Maranhão": "ma", "Mato Grosso": "mt", "Mato Grosso do Sul": "ms",
    "Minas Gerais": "mg", "Pará": "pa", "Paraíba": "pb", "Paraná": "pr",
    "Pernambuco": "pe", "Piauí": "pi", "Rio de Janeiro": "rj", "Rio Grande do Norte": "rn",
    "Rio Grande do Sul": "rs", "Rondônia": "ro", "Roraima": "rr", "Santa Catarina": "sc",
    "São Paulo": "sp", "Sergipe": "se", "Tocantins": "to"
}

with sync_playwright() as p:
    browser = p.firefox.launch(headless=True)
    page = browser.new_page()

    resultados = {}

    for estado, sigla in estados.items():
        try:
            page.goto("https://cidades.ibge.gov.br/", timeout=60000)
            search_box = page.get_by_placeholder("O que você procura?")
            search_box.fill(estado)
            page.wait_for_timeout(500)
            search_box.press("Backspace")
            page.wait_for_timeout(500)

            page.locator(f'a[href="/brasil/{sigla}"]').click()
            page.wait_for_url(f"**/brasil/{sigla}/panorama**", timeout=60000)

            dados_estado = extrair_dados_da_pagina(page)

            resultados[estado] = dados_estado
            print(f"Dados extraídos: {estado}")
        except Exception as e:
            print(f"Erro no estado {estado}: {e}")

    browser.close()

    with open("dados_estados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
