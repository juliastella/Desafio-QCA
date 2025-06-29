import json
from playwright.sync_api import sync_playwright, TimeoutError

# O dicionário TOPICOS e a lista ESTADOS permanecem os mesmos.
TOPICOS = {
    'População': [
        'População no último censo',
        'Densidade demográfica',
        'População estimada',
        'Total de veículos'
    ],
    'Educação': [
        'IDEB – Anos iniciais do ensino fundamental (Rede pública)',
        'IDEB – Anos finais do ensino fundamental (Rede pública)',
        'Matrículas no ensino fundamental',
        'Matrículas no ensino médio',
        'Docentes no ensino fundamental',
        'Número de estabelecimentos de ensino fundamental',
        'Número de estabelecimentos de ensino médio'
    ],
    'Trabalho e rendimento': [
        'Rendimento nominal mensal domiciliar per capita',
        'Pessoas de 16 anos ou mais ocupadas na semana de referência',
        'Proporção de pessoas de 16 anos ou mais em trabalho formal, considerando apenas as ocupadas na semana de referência',
        'Proporção de pessoas de 14 anos ou mais de idade, ocupadas na semana de referência em trabalhos formais',
        'Rendimento médio real habitual do trabalho principal das pessoas de 14 anos ou mais de idade, ocupadas na semana de referência em trabalhos formais',
        'Pessoal ocupado na Administração pública, defesa e seguridade social'
    ],
    'Economia': [
        'Índice de Desenvolvimento Humano Municipal (IDHM)',
        'Total de receitas brutas realizadas',
        'Total de despesas brutas empenhadas',
        'Número de agências',
        'Depósitos a prazo',
        'Depósitos à vista'
    ],
    'Território': [
        'Número de municípios',
        'Área da unidade territorial',
        'Área urbanizada'
    ]
}

ESTADOS = [
    'Acre', 'Alagoas', 'Amapá', 'Amazonas', 'Bahia', 'Ceará', 'Distrito Federal',
    'Espírito Santo', 'Goiás', 'Maranhão', 'Mato Grosso', 'Mato Grosso do Sul',
    'Minas Gerais', 'Pará', 'Paraíba', 'Paraná', 'Pernambuco', 'Piauí',
    'Rio de Janeiro', 'Rio Grande do Norte', 'Rio Grande do Sul', 'Rondônia',
    'Roraima', 'Santa Catarina', 'São Paulo', 'Sergipe', 'Tocantins'
]


def coletar_dados_ibge():
    """
    Função principal para orquestrar a coleta de dados.
    """
    resultados_finais = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Mude para False se quiser ver o navegador
        page = browser.new_page()

        for estado in ESTADOS:
            print(f"--- Iniciando coleta para: {estado} ---")
            dados_estado = {}
            try:
                # 1. NAVEGAÇÃO E BUSCA
                page.goto('https://cidades.ibge.gov.br/', timeout=60000)
                
                search_box = page.get_by_placeholder('O que você procura?')
                search_box.click()
                search_box.type(estado, delay=50) # delay para simular digitação humana
                
                # Aguardando o primeiro item do autocomplete ficar visível.
                primeiro_resultado = page.locator('.busca__auto-completar__resultado__item').first
                primeiro_resultado.wait_for(state="visible", timeout=5000)
                primeiro_resultado.click()
                
                # Aguarda a navegação para a página do estado
                page.wait_for_load_state('domcontentloaded', timeout=30000)
                print(f"Página de {estado} carregada.")
                
                # 2. ROLAGEM PARA CARREGAR TODO O CONTEÚDO
                page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                # Espera a rede ficar ociosa, garantindo que os dados carregados pela rolagem estejam prontos
                page.wait_for_load_state('networkidle', timeout=10000)
                print("Página rolada e conteúdo carregado.")

                # 3. EXTRAÇÃO DOS DADOS
                for topico, subtopicos in TOPICOS.items():
                    dados_estado[topico] = {}
                    for sub in subtopicos:
                        try:
                            # A estratégia de localização original
                            bloco = page.locator(f'.indicador:has(.indicador__nome:has-text("{sub}"))')
                            
                            # Espera curta para o bloco específico
                            bloco.first.wait_for(timeout=2000)
                            
                            valor_el = bloco.locator('.indicador__valor').first
                            valor_texto = valor_el.text_content().strip()
                            
                            dados_estado[topico][sub] = valor_texto
                        except TimeoutError:
                            dados_estado[topico][sub] = 'Não encontrado'
                
                resultados_finais.append({'estado': estado, **dados_estado})
                print(f"✅ Coleta para {estado} concluída com sucesso.")

            except Exception as e:
                print(f"❌ Erro com {estado}: {e}")
                resultados_finais.append({'estado': estado, 'erro': str(e)})

        browser.close()

    return resultados_finais


def salvar_resultados(resultados):
    """
    Salva os dados coletados no formato JSON.
    """
    print("\n--- Salvando resultados ---")
    
    # SALVAR EM JSON
    with open('dados_ibge.json', 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
    print("✅ Dados salvos em dados_ibge.json")


if __name__ == "__main__":
    dados_coletados = coletar_dados_ibge()
    if dados_coletados:
        salvar_resultados(dados_coletados)
