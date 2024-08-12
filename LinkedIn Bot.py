import os
import random
import time
import datetime
from datetime import datetime as dt
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from random import shuffle
from os.path import join, dirname
from dotenv import load_dotenv
from colorama import Fore, Style, init
from tqdm import tqdm

# Carregar variáveis de ambiente do arquivo .env
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Configurações
EMAIL = os.getenv("EMAIL", '')
PASSWORD = os.getenv("PASSWORD", '')

# Definir os tipos de usuários específicos para visualizar
SPECIFIC_USERS_TO_VIEW = (" ")


# Número de carregamentos preguiçosos (lazy loads) para realizar na página da rede
# Define quantas vezes o bot deve rolar a página para carregar novos perfis.
NUM_LAZY_LOAD_ON_MY_NETWORK_PAGE = 10

# Configura se o bot deve conectar-se automaticamente com os usuários encontrados
# Se definido como True, o bot tentará conectar-se com os perfis que visita.
CONNECT_WITH_USERS = True

# Configura se as conexões com os usuários devem ser feitas de forma aleatória
# Se definido como True, o bot decidirá aleatoriamente se vai conectar com um perfil ou não.
RANDOMIZE_CONNECTING_WITH_USERS = True

# Lista de cargos para os quais o bot deve tentar se conectar
# Define quais cargos específicos o bot deve buscar ao se conectar com perfis.
JOBS_TO_CONNECT_WITH = [' ']

# Configura se o bot deve endossar conexões existentes
# Se definido como True, o bot endossará habilidades de conexões que já foram feitas.
ENDORSE_CONNECTIONS = False

# Configura se o endosse das conexões deve ser feito de forma aleatória
# Se definido como True, o bot decidirá aleatoriamente se vai endossar uma conexão ou não.
RANDOMIZE_ENDORSING_CONNECTIONS = False

# Configura se informações detalhadas devem ser exibidas no console
# Se definido como True, o bot exibirá informações detalhadas sobre suas operações.
VERBOSE = False

def timestamp():
    """Retorna o timestamp atual."""
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def Launch():
    """
    Inicia o bot LinkedIn utilizando o Chrome.
    """

    # Verificar se o arquivo 'VisitedUsers.txt' existe, caso contrário, criar
    if not os.path.isfile('VisitedUsers.txt'):
        with open('VisitedUsers.txt', 'w') as VisitedUsersFile:
            pass

    # Iniciar o Chrome automaticamente.
    StartBrowser()

def StartBrowser():
    """
    Inicia o navegador Chrome e faz login no LinkedIn.
    """

    print(Fore.GREEN + '\nIniciando o Chrome' + Fore.RESET)
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service)

    # Configurar o zoom do navegador para 80%
    browser.execute_script("document.body.style.zoom='80%'")

    # Fazer login no LinkedIn
    browser.get('https://linkedin.com/uas/login')
    emailElement = browser.find_element('id', 'username')
    emailElement.send_keys(EMAIL)
    passElement = browser.find_element('id', 'password')
    passElement.send_keys(PASSWORD)
    passElement.submit()

    print('Fazendo login...')
    time.sleep(3)

    # Configurar o zoom do navegador para 70%
    browser.execute_script("document.body.style.zoom='70%'")


    # Verificar se o login foi bem-sucedido
    soup = BeautifulSoup(browser.page_source, "html.parser")
    if soup.find('div', {'class': 'alert error'}):
        print(Fore.RED + 'Erro! Verifique seu nome de usuário e senha.' + Fore.RESET)
        browser.quit()
    elif browser.title == '403: Forbidden':
        print(Fore.RED + 'LinkedIn está momentaneamente indisponível. Aguarde um momento e tente novamente.' + Fore.RESET)
        browser.quit()
    else:
        print(Fore.GREEN + 'Login bem-sucedido!' + Fore.RESET)
        LinkedInBot(browser)

def HideMessagesBox(browser):
    # Usar o XPath para localizar e interagir com o botão
    try:
        # Tente encontrar o elemento e ocultá-lo
        element = browser.find_element(By.CLASS_NAME, "application-outlet__overlay-container")
        browser.execute_script("arguments[0].style.display = 'none';", element)
        if VERBOSE:
            print("O elemento 'caixa de mensagens' foi ocultado com sucesso.")
    except NoSuchElementException:
        if VERBOSE:
            print("O elemento 'caixa de mensagens' não foi encontrado na página.")

def LinkedInBot(browser):
    """
    Executa o bot LinkedIn para visitar e conectar-se com perfis.
    browser: o driver Selenium usado para executar o bot.
    VERBOSE: booleano que controla o nível de detalhes das mensagens.
    """
    T = 0
    V = 0
    profilesQueued = []
    error403Count = 0
    timer = time.time()

    # Call HMB function
    HideMessagesBox(browser)

    if ENDORSE_CONNECTIONS:
        EndorseConnections(browser)

    if VERBOSE:
        print(Fore.GREEN + 'Na página "Minha rede" para capturar URLs de usuários...\n' + Fore.RESET)
    if not VERBOSE:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {Fore.GREEN}Capturando URLs de usuários...\n" + Fore.RESET)

    # Loop infinito para visitar perfis
    while True:
        while True:
            NavigateToMyNetworkPage(browser)
            T += 1

            if GetNewProfileURLS(BeautifulSoup(browser.page_source, "html.parser"), profilesQueued):
                break
            else:
                if VERBOSE:
                    print(Fore.CYAN + '| Tentativa de captura de URLs de usuários falhou. Tentando novamente...' + Fore.RESET)
                if not VERBOSE:
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] {Fore.CYAN}Tentativa de captura falhou, tentando novamente..." + Fore.RESET)
                time.sleep(random.uniform(15, 45))

        # Atualizar a lista de URLs de perfis
        soup = BeautifulSoup(browser.page_source, "html.parser")
        profilesQueued = list(set(GetNewProfileURLS(soup, profilesQueued)))

        V += 1
        if VERBOSE:
            print(Fore.GREEN + f'\n\nObtivemos {len(profilesQueued)} usuários para começar a visualizar!\n' + Fore.RESET)
        if not VERBOSE:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {Fore.GREEN}Usuários capturados. Iniciando visualização...\n" + Fore.RESET)
        print(browser.title.replace(' | LinkedIn', '').replace('(', '').replace(')', ''), ' visitado. T:', T, '| V:', V, '| Q:', len(profilesQueued))

        # Visitar e interagir com os perfis
        while profilesQueued:
            random.shuffle(profilesQueued)
            profileID = profilesQueued.pop()
            browser.get(profileID)
            
            # Aguarde até que a página seja totalmente carregada
            time.sleep(5)

            if CONNECT_WITH_USERS:
                if not RANDOMIZE_CONNECTING_WITH_USERS:
                    ConnectWithUser(browser)
                elif random.choice([True, False]):
                    ConnectWithUser(browser)

            # Registrar o perfil visitado
            with open('VisitedUsers.txt', 'a') as VisitedUsersFile:
                VisitedUsersFile.write(profileID + '\r\n')

            time.sleep(30)
            soup = BeautifulSoup(browser.page_source, "html.parser")
            profilesQueued.extend(GetNewProfileURLS(soup, profilesQueued))
            profilesQueued = list(set(profilesQueued))

            # Verificar o título da página e lidar com erros
            browserTitle = browser.title.encode('ascii', 'ignore').decode('ascii').replace('  ', ' ')

            if browserTitle == '403: Forbidden':
                error403Count += 1
                pause_duration = 3600 * error403Count + (random.randrange(0, 10)) * 60
                resume_time = datetime.datetime.now() + datetime.timedelta(seconds=pause_duration)
                if VERBOSE:
                    print(f'{Fore.WHITE}[{timestamp}] {Fore.RED}Erro 403: LinkedIn está momentaneamente indisponível. Pausando por {int(pause_duration / 3600)} hora(s).' + Fore.RESET)
                    print(f'{Fore.WHITE}[{timestamp}] {Fore.RED}O bot retornará às {resume_time.strftime("%H:%M:%S")}' + Fore.RESET)
                if not VERBOSE:
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] {Fore.RED}Erro 403: Pausando por tempo definido." + Fore.RESET)
                time.sleep(pause_duration)
                timer = time.time()

            elif browserTitle == 'Profile | LinkedIn':
                T += 1
                error403Count = 0
                if VERBOSE:
                    print(f'{Fore.YELLOW}Usuário não está na sua rede. T: {T} | V: {V} | Q: {len(profilesQueued)}' + Fore.RESET)
                if not VERBOSE:
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] {Fore.YELLOW}Usuário fora da rede, prosseguindo..." + Fore.RESET)
            
            else:
                T += 1
                V += 1
                now = datetime.datetime.now()
                timestamp = now.strftime("%H:%M:%S")
                if VERBOSE:
                    print(f"{browserTitle.replace(' | LinkedIn', '')} visitado. T: {T} | V: {V} | Q: {len(profilesQueued)}")
                if not VERBOSE:
                    print(f"[{timestamp}] {Fore.CYAN}Perfil visitado: {browserTitle.replace(' | LinkedIn', '')}. T: {T} | V: {V} | Q: {len(profilesQueued)}" + Fore.RESET)

            # Verifica se é necessário pausar para evitar sobrecarga e evitar bloqueio de IP
            if (T % 7 == 0) or time.time() - timer > 600:
                pause_duration = 90 + (random.randrange(1, 10)) * 60
                resume_time = datetime.datetime.now() + datetime.timedelta(seconds=pause_duration)
                if VERBOSE:
                    print(f'[{timestamp}] {Fore.RED}Pausando por {int(pause_duration)} segundos para evitar bloqueio de IP. O bot retornará às {resume_time.strftime("%H:%M:%S")}.\n' + Fore.RESET)
                if not VERBOSE:
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] {Fore.RED}Pausando por segurança. Retorno às {resume_time.strftime('%H:%M:%S')}\n" + Fore.RESET)
                time.sleep(pause_duration)
                timer = time.time()
            else:
                pause_duration = random.uniform(30, 180)
                resume_time = datetime.datetime.now() + datetime.timedelta(seconds=pause_duration)
                if VERBOSE:
                    print(f'[{timestamp}] Pausando por {int(pause_duration)} segundos. O bot retornará às {resume_time.strftime("%H:%M:%S")}\n')
                if not VERBOSE:
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] {Fore.CYAN}Pausa rápida. Retorno às {resume_time.strftime('%H:%M:%S')}\n" + Fore.RESET)
                time.sleep(pause_duration)

        if VERBOSE:
            print(f'{Fore.WHITE}[{timestamp}]{Fore.RESET} {Fore.RED}Não há mais perfis para visitar. Reiniciando com a página da rede...\n' + Fore.RESET)
        if not VERBOSE:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {Fore.RED}Reiniciando ciclo de visitas e indo para a pagina de rede.\n" + Fore.RESET)

def NavigateToMyNetworkPage(browser):
    """
    Navigate to the my network page and scroll to the bottom and let the lazy loading
    go to be able to grab more potential users in your network. It is reccommended to
    increase the NUM_LAZY_LOAD_ON_MY_NETWORK_PAGE value if you are using the variable
    SPECIFIC_USERS_TO_VIEW.
    browser: the selenium browser used to interact with the page.
    """

    browser.get('https://www.linkedin.com/mynetwork/')

    # Wait for 5 seconds to allow the page to load before hiding the message box
    time.sleep(5)
    #Call HMB function
    HideMessagesBox(browser)

    for counter in range(1, NUM_LAZY_LOAD_ON_MY_NETWORK_PAGE):
        ScrollToBottomAndWaitForLoad(browser)

def ConnectWithUser(browser):
    """
    Connect with the user viewing if their job title is found in your list of roles
    you want to connect with.
    browser: the selenium browser used to interact with the page.
    """
    
    # Inicializar o timestamp
    timestamp = dt.now().strftime('%H:%M:%S')

    try:
        # Verificar o título da página e lidar com erros
        if VERBOSE:
            print(f'{Fore.WHITE}[{timestamp}] {Fore.CYAN} Retrieving browser title.{Fore.RESET}')
        
        browserTitle = browser.title.encode('ascii', 'ignore').decode('ascii').replace('  ', ' ')

        if VERBOSE:
            print(f'{Fore.WHITE}[{timestamp}] {Fore.CYAN} Browser title obtained: "{browserTitle}".{Fore.RESET}')
        if not VERBOSE:
            print(f'{Fore.WHITE}[{timestamp}] {Fore.CYAN} Checking browser title.{Fore.RESET}')

        soup = BeautifulSoup(browser.page_source, "html.parser")
        jobTitleMatches = False

        if VERBOSE:
            print(f'{Fore.WHITE}[{timestamp}] {Fore.CYAN} Waiting for the page to load.{Fore.RESET}')
        
        # Wait for 5 seconds to allow the page to load before hiding the message box
        time.sleep(5)

        if VERBOSE:
            print(f'{Fore.WHITE}[{timestamp}] {Fore.CYAN} Hiding messages box.{Fore.RESET}')

        # Call HMB function
        HideMessagesBox(browser)

        if VERBOSE:
            print(f'{Fore.WHITE}[{timestamp}] {Fore.CYAN} Searching for user job titles on the page.{Fore.RESET}')
        if not VERBOSE:
            print(f'{Fore.WHITE}[{timestamp}] {Fore.CYAN} Checking for job title matches.{Fore.RESET}')

        # Encontrar o título do trabalho no <div> com a classe 'text-body-medium break-words'
        for div in soup.find_all('div', class_='text-body-medium break-words'):
            if VERBOSE:
                print(f'{Fore.WHITE}[{timestamp}] {Fore.CYAN} Checking job title: "{div.get_text()}".{Fore.RESET}')
            
            for job in JOBS_TO_CONNECT_WITH:
                if job.upper() in div.get_text().upper():
                    jobTitleMatches = True
                    if VERBOSE:
                        print(f'{Fore.WHITE}[{timestamp}] {Fore.GREEN} Match found for job title: "{job}".{Fore.RESET}')
                    break

        if jobTitleMatches:
            try:
                if VERBOSE:
                    print(f'{Fore.WHITE}[{timestamp}] {Fore.YELLOW} Sending the user an invitation to connect.{Fore.RESET}')
                if not VERBOSE:
                    print(f'{Fore.WHITE}[{timestamp}] {Fore.YELLOW} Invitation being sent.{Fore.RESET}')

                # Usar XPath atualizado para clicar no botão "Conectar"
                browser.find_element("xpath", '//div[3]/div/button/span').click()
                
                if VERBOSE:
                    print(f'{Fore.WHITE}[{timestamp}] {Fore.YELLOW} Clicked "Connect" button.{Fore.RESET}')
                if not VERBOSE:
                    print(f'{Fore.WHITE}[{timestamp}] {Fore.YELLOW} Connect button clicked.{Fore.RESET}')

                # Usar XPath atualizado para clicar no botão "Confirm send invitation"
                time.sleep(5)
                #ou tentar esse na linha 396. 110824 19h41 //span[contains(.,'Send without a note')]
                browser.find_element("xpath", '//button[2]/span').click()

                if VERBOSE:
                    print(f'{Fore.WHITE}[{timestamp}] {Fore.YELLOW} Clicked "Send without a note" button.{Fore.RESET}')
                if not VERBOSE:
                    print(f'{Fore.WHITE}[{timestamp}] {Fore.YELLOW} Send without a note button clicked.{Fore.RESET}')
                
                # Confirmar o envio da solicitação usando o XPath fornecido
                time.sleep(5)
                confirmation_message = browser.find_element("xpath", '//h3[contains(.,"Your invitation is sent")]')

                if VERBOSE:
                    print(f'{Fore.WHITE}[{timestamp}] {Fore.GREEN} Invitation sent successfully to "{browserTitle}".{Fore.RESET}')
                    print(f'{Fore.WHITE}[{timestamp}] {Fore.GREEN} Confirmation message: {confirmation_message.text}.{Fore.RESET}')
                if not VERBOSE:
                    print(f'{Fore.WHITE}[{timestamp}] {Fore.GREEN} Invitation sent.{Fore.RESET}')
                    print(f'{Fore.WHITE}[{timestamp}] {Fore.GREEN} Confirmation message: {confirmation_message.text}.{Fore.RESET}')

            except Exception as e:
                print(f'{Fore.RED}[{timestamp}] An error occurred: {e}{Fore.RESET}')
        else:
            if VERBOSE:
                print(f'{Fore.WHITE}[{timestamp}] {Fore.CYAN} No matching job titles found. No action taken.{Fore.RESET}')
            if not VERBOSE:
                print(f'{Fore.WHITE}[{timestamp}] {Fore.CYAN} No matches found.{Fore.RESET}')

    except Exception as e:
        # Captura qualquer exceção não tratada para garantir que `timestamp` seja acessível
        print(f'{Fore.RED}[{timestamp}] An error occurred: {e}{Fore.RESET}')

def GetNewProfileURLS(soup, profilesQueued):
    """
    Pega mais perfis em pesfis visitados para serem visitados.
    Get new profile urls to add to the navigate queue.
    soup: beautiful soup instance of page's source code.
    profileQueued: current list of profile queues.
    """

    # Open, load and close
    with open('VisitedUsers.txt', 'r') as VisitedUsersFile:
        VisitedUsers = [line.strip() for line in VisitedUsersFile]
    VisitedUsersFile.close()

    profileURLS = []
    profileURLS.extend(FindProfileURLsInNetworkPage(
        soup, profilesQueued, profileURLS, VisitedUsers))
    profileURLS.extend(FindProfileURLsInPeopleAlsoViewed(
        soup, profilesQueued, profileURLS, VisitedUsers))
    profileURLS.extend(FindProfileURLsInEither(
        soup, profilesQueued, profileURLS, VisitedUsers))
    profileURLS.extend(FindPremiumPeerSuggestion(
        soup, profilesQueued, profileURLS, VisitedUsers))
    profileURLS = list(set(profileURLS))

    return profileURLS


def FindProfileURLsInNetworkPage(soup, profilesQueued, profileURLS, VisitedUsers):
    """
    Obtém novas URLs de perfis para adicionar à fila de navegação a partir da página da minha rede.
    soup: instância do BeautifulSoup do código-fonte da página.
    profileQueued: lista atual de perfis na fila.
    profileURLS: URLs de perfis já encontradas nesta raspagem.
    VisitedUsers: perfis de usuários que já visualizamos.
    """
    
    newProfileURLS = []
    
    try:
        # Itera sobre todos os links de perfis na página.
        for a in soup.find_all('a', class_='discover-entity-type-card__link'):
            # Verifica se o URL é válido e não está na lista de perfis visitados ou já encontrados.
            if ValidateURL(a['href'], profileURLS, profilesQueued, VisitedUsers):
                
                # Se houver uma lista específica de ocupações para visualizar, verifica se a ocupação do perfil corresponde.
                if SPECIFIC_USERS_TO_VIEW:
                    for span in a.find_all('span', class_='discover-person-card__occupation'):
                        for occupation in SPECIFIC_USERS_TO_VIEW:
                            if occupation.lower() in span.text.lower():
                                if VERBOSE:
                                    print(f'Encontrado perfil com ocupação específica: {a["href"]}')
                                newProfileURLS.append(a['href'])
                                break

                # Caso não haja uma lista específica de ocupações, adiciona o perfil à lista de novos perfis.
                else:
                    if VERBOSE:
                        print(f'Perfil encontrado: {a["href"]}')
                    newProfileURLS.append(a['href'])
    except Exception as e:
        # Caso ocorra qualquer exceção, imprime o erro para depuração.
        if VERBOSE:
            print(f'Ocorreu um erro ao buscar URLs de perfis: {e}')

    return newProfileURLS


def FindProfileURLsInPeopleAlsoViewed(soup, profilesQueued, profileURLS, VisitedUsers):
    """
    Obtém novas URLs de perfis para adicionar à fila de navegação a partir da seção 'Pessoas também visualizadas'.
    soup: instância do BeautifulSoup do código-fonte da página.
    profilesQueued: lista atual de perfis na fila.
    profileURLS: URLs de perfis já encontradas nesta raspagem.
    VisitedUsers: perfis de usuários que já visualizamos.
    """
    
    newProfileURLS = []
    
    try:
        # Tenta encontrar todos os links de perfil na seção 'Pessoas também visualizadas' com a classe correta.
        # for a in soup.find_all('a', class='optional-action-target-wrapper'):
        for a in soup.find_all('a', attrs={'data-field': 'browsemap_card_click'}):
            if 'href' in a.attrs:  # Verifica se o atributo 'href' está presente
                profile_url = a['href']
                
                parsed_url = urlparse(profile_url)
                profile_url_cleaned = parsed_url._replace(query='').geturl()
                
                if VERBOSE:
                    print(f'{Fore.LIGHTBLACK_EX}URL original:{Style.RESET_ALL} {profile_url}')
                    print(f'{Fore.LIGHTCYAN_EX}URL limpa:{Style.RESET_ALL} {profile_url_cleaned}')
                
                if ValidateURL(profile_url_cleaned, profileURLS, profilesQueued, VisitedUsers):
                    if SPECIFIC_USERS_TO_VIEW:
                        # Verifica se algum dos textos específicos está presente nos elementos 'div'
                        for div in a.find_all('div'):
                            for occupation in SPECIFIC_USERS_TO_VIEW:
                                if occupation.lower() in div.text.lower():
                                    if VERBOSE:
                                        print(f'Perfil com ocupação específica encontrado: {profile_url_cleaned}')
                                    newProfileURLS.append(profile_url_cleaned)
                                    break
                    else:
                        if VERBOSE:
                            print(f'Perfil encontrado: {profile_url_cleaned}')
                        newProfileURLS.append(profile_url_cleaned)
    except Exception as e:
        # Em caso de erro, imprime a mensagem de erro.
        if VERBOSE:
            print(f'Ocorreu um erro ao buscar URLs de perfis: {e}')

    return newProfileURLS

def FindProfileURLsInEither(soup, profilesQueued, profileURLS, VisitedUsers):
    """
    Obtém novas URLs de perfis para adicionar à fila de navegação, algumas usando nomes de classe diferentes
    na página de minha rede e na seção 'Pessoas também visualizadas'.
    soup: instância do BeautifulSoup do código-fonte da página.
    profilesQueued: lista atual de perfis na fila.
    profileURLS: URLs de perfis já encontradas nesta raspagem.
    VisitedUsers: perfis de usuários que já visualizamos.
    """

    newProfileURLS = []

    try:
        # Encontra todas as listas não ordenadas com a classe específica
        for ul in soup.find_all('ul', class_='pv-profile-section__section-info'):
            if VERBOSE:
                print('Processando lista de perfis encontrada.')

            for li in ul.find_all('li'):
                a = li.find('a')
                if a and 'href' in a.attrs:  # Verifica se o link e o atributo 'href' estão presentes
                    profile_url = a['href']
                    
                    if VERBOSE:
                        print(f'URL encontrada: {profile_url}')
                    
                    if ValidateURL(profile_url, profileURLS, profilesQueued, VisitedUsers):
                        if SPECIFIC_USERS_TO_VIEW:
                            # Verifica se algum dos textos específicos está presente nos elementos 'div'
                            for div in a.find_all('div'):
                                for occupation in SPECIFIC_USERS_TO_VIEW:
                                    if occupation.lower() in div.text.lower():
                                        if VERBOSE:
                                            print(f'Perfil com ocupação específica encontrado: {profile_url}')
                                        profileURLS.append(profile_url)
                                        break
                        else:
                            if VERBOSE:
                                print(f'Perfil adicionado: {profile_url}')
                            profileURLS.append(profile_url)
    except Exception as e:
        # Em caso de erro, imprime a mensagem de erro.
        if VERBOSE:
            print(f'Ocorreu um erro ao buscar URLs de perfis: {e}')

    return newProfileURLS

def FindPremiumPeerSuggestion(soup, profilesQueued, profileURLS, VisitedUsers):
    """
    Get new profile URLs from premium peer suggestions.
    soup: beautiful soup instance of page's source code.
    profilesQueued: current list of profile queues.
    profileURLS: profile URLs already found this scrape.
    VisitedUsers: user's profiles that we have already viewed.
    VERBOSE: whether to print debug information.
    """

    newProfileURLS = []

    try:
        elements_found = True  # Flag to check if any element was found
        
        # Encontre todos os links que contêm o atributo data-field="premium_spotlight_card_click"
        for a in soup.find_all('a', attrs={'data-field': 'premium_spotlight_card_click'}):
            elements_found = True
            href = a.get('href')
            
            if VERBOSE:
                if href:
                    print(f"Premium user found, processing URL: {href}")
                else:
                    print("Noremium user found, and no 'href' attribute found in the element, skipping.")

            # Ignore the element if 'href' is not found
            if not href:
                continue

            # Validate the URL and add to list if valid
            if ValidateURL(href, profileURLS, profilesQueued, VisitedUsers):
                if VERBOSE:
                    print(f"Valid URL found: {href}")
                newProfileURLS.append(href)
            elif VERBOSE:
                print(f"Invalid or already processed URL: {href}")

        if VERBOSE and not elements_found:
            print("No elements with 'data-field=\"premium_spotlight_card_click\"' were found.")

    except Exception as e:
        if VERBOSE:
            print(f"An error occurred: {e}")

    return newProfileURLS


def ValidateURL(url, profileURLS, profilesQueued, VisitedUsers):
    """
    Validate the url passed meets requirement to be navigated to.
    profileURLS: list of urls already added within the GetNewProfileURLS method to be returned.
        Want to make sure we are not adding duplicates.
    profilesQueued: list of urls already added and being looped. Want to make sure we are not
        adding duplicates.
    VisitedUsers: users already visited. Don't want to be creepy and visit them multiple days in a row.
    """

    return (url not in profileURLS 
            and url not in profilesQueued 
            and "/in/" in url 
            and "/connections/" not in url 
            and "/skills/" not in url 
            and "/company/" not in url 
            and "/search/" not in url 
            and "/groups/" not in url 
            and "/newsletters/" not in url
            and url not in VisitedUsers)

def EndorseConnections(browser):
    """
    Endossa habilidades para suas conexões encontradas. Isso só curte as três habilidades mais populares
    que o usuário endossou. Se as pessoas quiserem, este recurso pode ser expandido. Basta postar um pedido de melhoria no repositório.
    browser: instância do navegador para interação com a página.
    """

    print("Coletando URLs das suas conexões para endossar suas habilidades.")
    profileURLS = []
    
    # Acessa a página de conexões
    browser.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    time.sleep(3)

    try:
        # Realiza a rolagem para baixo e espera o carregamento da página para carregar mais conexões
        for counter in range(1, NUM_LAZY_LOAD_ON_MY_NETWORK_PAGE):
            print(f"Rolagem para baixo, carregamento número: {counter}")
            ScrollToBottomAndWaitForLoad(browser)

        # Obtém o conteúdo da página e analisa com BeautifulSoup
        soup = BeautifulSoup(browser.page_source, "html.parser")
        print("Coletando URLs dos perfis das conexões.")
        for a in soup.find_all('a', class_='mn-person-info__picture'):
            if VERBOSE:
                print(f'URL do perfil encontrado: {a["href"]}')
            profileURLS.append(a['href'])

        print("Endossando habilidades das suas conexões.")

        # Itera sobre cada URL de perfil para endossar habilidades
        for url in profileURLS:
            endorseConnection = True
            if RANDOMIZE_ENDORSING_CONNECTIONS:
                endorseConnection = random.choice([True, False])
                print(f"Decisão aleatória para endossar a conexão: {endorseConnection}")

            if endorseConnection:
                fullURL = url
                # fullURL = 'https://www.linkedin.com'+url
                if VERBOSE:
                    print(f'Endossando a conexão {fullURL}')

                # Acessa o perfil da conexão
                browser.get(fullURL)
                time.sleep(3)
                
                # Clica nos botões de endossar habilidades
                for button in browser.browser.find_element("xpath", '//button[@data-control-name="endorse"]'):
                    print("Clicando no botão de endossar habilidade.")
                    button.click()
                    
    except Exception as e:
        # Imprime a mensagem de erro em caso de exceção
        print(f'Ocorreu uma exceção ao endossar suas conexões: {e}')
    
    print('Processo de endosse concluído.')


def ScrollToBottomAndWaitForLoad(browser):
    """
    Scroll to the bottom of the page and wait for the page to perform its lazy loading.
    browser: selenium webdriver used to interact with the browser.
    """

    if VERBOSE:
        print("Executing script to scroll to the bottom of the page.")

    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    if VERBOSE:
        print("Waiting for 5 seconds to allow lazy loading to complete.")

    time.sleep(5)

    if VERBOSE:
        print("Finished waiting after scrolling. Ready for next operations.")


if __name__ == '__main__':
    Launch()
