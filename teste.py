from playwright.sync_api import sync_playwright, TimeoutError

# O 'with' garante que os recursos do Playwright sejam fechados corretamente
with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)
    page = browser.new_page()

    # --- ETAPA 1: NAVEGAÇÃO ---
    print("Iniciando navegação...")
    try:
        page.goto("https://cidades.ibge.gov.br/", timeout=60000)
        search_box = page.get_by_placeholder("O que você procura?")
        search_box.fill("Pernambuco")
        page.wait_for_timeout(500)
        search_box.press("Backspace")
        page.wait_for_timeout(500)
        page.locator('a[href="/brasil/pe"]').click()
        page.wait_for_url("**/brasil/pe/panorama**", timeout=60000)
        print("Navegação concluída com sucesso.")
    except Exception as e:
        print(f"Ocorreu um erro durante a navegação: {e}")
        browser.close()
        exit()

    # --- ETAPA 2: ESPERAR PELO ÍCONE (GARANTIR QUE A SEÇÃO CARREGOU) ---
    print("\nAguardando a seção de população carregar...")
    icone_selector = "span.ico.ico-populacao"
    try:
        page.wait_for_selector(icone_selector, state="visible", timeout=15000)
        print("OK! Ícone de população está visível.")
    except TimeoutError:
        print("FALHA: A seção de população não carregou a tempo. Encerrando.")
        browser.close()
        exit()

    # --- ETAPA 3: CONTAR QUANTAS CLASSES "lista_indicador" EXISTEM ---
    print("\nIniciando a contagem dos elementos 'lista_indicador'...")
    
    # Define o seletor para as linhas que queremos contar
    seletor_do_indicador = "tr.lista_indicador"
    
    # Usa o locator para encontrar TODOS os elementos que correspondem ao seletor
    elementos_encontrados = page.locator(seletor_do_indicador)
    
    # Usa o método .count() para obter a quantidade
    quantidade = elementos_encontrados.count()
    
    print("\n=============================================================")
    print(f"      CONTAGEM FINAL: {quantidade}      ")
    print(f"Foram encontrados {quantidade} elementos com a classe 'lista_indicador'.")
    print("=============================================================")
    
    print("\nO navegador ficará aberto por 10 segundos para sua verificação.")
    page.wait_for_timeout(10000)
    browser.close()
    print("Script de contagem finalizado.")