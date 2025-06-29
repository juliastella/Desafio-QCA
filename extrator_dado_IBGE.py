from playwright.sync_api import sync_playwright
import json
import re
import time
import traceback


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


estados = {
    "Acre": "ac", "Alagoas": "al", "Amapá": "ap", "Amazonas": "am",
    "Bahia": "ba", "Ceará": "ce", "Distrito Federal": "df", "Espírito Santo": "es",
    "Goiás": "go", "Maranhão": "ma", "Mato Grosso": "mt", "Mato Grosso do Sul": "ms",
    "Minas Gerais": "mg", "Pará": "pa", "Paraíba": "pb", "Paraná": "pr",
    "Pernambuco": "pe", "Piauí": "pi", "Rio de Janeiro": "rj", "Rio Grande do Norte": "rn",
    "Rio Grande do Sul": "rs", "Rondônia": "ro", "Roraima": "rr", "Santa Catarina": "sc",
    "São Paulo": "sp", "Sergipe": "se", "Tocantins": "to"
}


def coletar_dados_estaduais():
    resultados = {}
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)  
        page = browser.new_page()

        for estado, sigla in estados.items():
            print(f"[INFO] Coletando dados de {estado} ({sigla.upper()})...")
            try:
                page.goto("https://cidades.ibge.gov.br/", timeout=60000)
                search_box = page.get_by_placeholder("O que você procura?")
                search_box.fill(estado)
                page.wait_for_timeout(500)
                search_box.press("Backspace")
                page.wait_for_timeout(500)

                link = page.locator(f'a[href="/brasil/{sigla}"]')
                if link.count() > 0:
                    link.first.wait_for(state="visible", timeout=20000)
                    link.first.click()
                else:
                    lista_resultado = page.locator(".busca__lista a").first
                    if lista_resultado:
                        print(f"[INFO] Usando primeiro resultado da busca para {estado}")
                        lista_resultado.wait_for(state="visible", timeout=20000)
                        lista_resultado.click()
                    else:
                        print(f"[WARN] Nenhum link encontrado para {estado}")
                        continue

                page.wait_for_url(f"**/brasil/{sigla}/panorama**", timeout=60000)
                dados_estado = extrair_dados_da_pagina(page)
                resultados[estado] = dados_estado
                print(f"[OK] Dados coletados de {estado}")
                time.sleep(1.5)

            except Exception as e:
                print(f"[ERRO] Estado {estado}: {e}")
                traceback.print_exc()

        browser.close()

    return resultados


if __name__ == "__main__":
    dados = coletar_dados_estaduais()

    with open("dados_estados.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

    print("[FINALIZADO] Dados salvos em 'dados_estados.json'")
