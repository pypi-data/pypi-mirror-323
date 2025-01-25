import requests
import sys
import os

def update_progress(current, total):
    """
    Atualiza uma barra de progresso no terminal.

    :param current: Número atual do progresso.
    :param total: Total de passos para completar.
    """
    porcentagem = (current / total) * 100
    barras = int((porcentagem / 100) * 50)
    sys.stdout.write(f"\r[{'#' * barras}{'.' * (50 - barras)}] {porcentagem:.2f}% ({current}/{total})")
    sys.stdout.flush()

class InovyoAPIClient:
    def __init__(self, api_token: str = None, api_secret: str = None):
        """
        Inicializa o cliente da API com o token e segredo de autenticação.
        
        :param api_token: O token de autenticação da API (opcional).
        :param api_secret: O segredo da API usado para autenticação (opcional).
        """
        # Verifica se as variáveis de ambiente estão definidas
        if api_token is None:
            api_token = os.getenv('INOVYO_KEY')
        if api_secret is None:
            api_secret = os.getenv('INOVYO_SECRET')

        if api_token is None or api_secret is None:
            raise ValueError("As credenciais da API devem ser fornecidas, seja como argumentos ou através das variáveis de ambiente.")

        self.api_token = api_token
        self.api_secret = api_secret
        self.token = None
        self.auth = False
        self.refresh_token()

    def refresh_token(self):
        """
        Renova automaticamente o JWT (token de autenticação) da API.

        Este método envia uma requisição POST para a API, passando o `api_token` e `api_secret`
        para obter um novo token de autenticação JWT.
        """
        url = "https://api.inovyo.com/v2/auth"
        payload = {
            "expire": 60,
            "api_token": self.api_token,
            "api_secret": self.api_secret
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data.get('token')
            self.auth = True
        else:
            raise Exception(f"Falha na autenticação: {response.status_code} - {response.text}")

    def verify_token(self):
        """
        Verifica se o token de autenticação atual é válido.

        :return: Um dicionário indicando se o token é válido ou não.
        :raises: Exception se o token não for válido.
        """
        url = "https://api.inovyo.com/v2/verify_token"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response = requests.get(url, headers=headers)
        while response.status_code == 401 and self.auth:
            self.refresh_token()
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return {"message": "Token válido", "status": "success"}
        else:
            raise Exception(f"Erro na verificação do token: {response.status_code} - {response.text}")

    def list_surveys(self, status: str = None, division: str = None):
        """
        Lista todas as pesquisas disponíveis na API.

        :param status: O status das pesquisas a ser filtrado (opcional). Pode ser 'active', 'inactive', etc.
        :param division: A divisão das pesquisas a ser filtrada (opcional).
        
        :return: Um dicionário com os dados das pesquisas.
        """
        url = f"https://api.inovyo.com/v2/survey/"
        params = {}
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        if status:
            params['status'] = status
        if division:
            params['division'] = division

        response = requests.get(url, params=params, headers=headers)
        while response.status_code == 401 and self.auth:
            self.refresh_token()
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            response = requests.get(url, params=params, headers=headers)

        return response.json()

    def get_responses(self, survey_id: str, start_date: str = None, end_date: str = None, order: str = None):
        """
        Obtém todas as respostas de uma pesquisa, com paginação automática.

        :param survey_id: O ID da pesquisa para a qual as respostas serão recuperadas.
        :param start_date: A data de início para filtrar as respostas (opcional).
        :param end_date: A data de fim para filtrar as respostas (opcional).
        :param order: A ordem das respostas (opcional). Pode ser 'asc' ou 'desc'.
        
        :return: Uma lista com todas as respostas da pesquisa.
        """
        url = f"https://api.inovyo.com/v2/survey/{survey_id}/responses"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            'limit': 1000
        }
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if order:
            params['order'] = order

        # Faz a primeira requisição
        response = requests.get(url, params=params, headers=headers)
        while response.status_code == 401 and self.auth:
            self.refresh_token()
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            response = requests.get(url, params=params, headers=headers)

        # Processa a resposta inicial
        response_data = response.json()
        all_responses = response_data.get('data', [])
        total_pages = response_data.get('total_pages', 1)  # Assume 1 página se 'total_pages' não existir

        update_progress(1, total_pages)
        for page in range(2, total_pages + 1):
            params['page'] = page
            response = requests.get(url, params=params, headers=headers)
            while response.status_code == 401 and self.auth:
                self.refresh_token()
                headers = {
                    "Authorization": f"Bearer {self.token}"
                }
                response = requests.get(url, params=params, headers=headers)
            response_data = response.json()
            all_responses.extend(response_data.get('data', []))
            update_progress(page, total_pages)

        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()
        return all_responses

    def get_all_responses(self, start_date: str = None, end_date: str = None, order: str = None):
        """
        Obtém todas as respostas de todas as pesquisas.

        Este método lista todas as pesquisas disponíveis e, para cada uma delas,
        recupera as respostas, realizando a paginação conforme necessário.
        
        :param survey_id: O ID da pesquisa para a qual as respostas serão recuperadas.
        :param start_date: A data de início para filtrar as respostas (opcional).
        :param end_date: A data de fim para filtrar as respostas (opcional).
        :param order: A ordem das respostas (opcional). Pode ser 'asc' ou 'desc'.
        :return: Uma lista contendo todas as respostas de todas as pesquisas.
        """
        surveys = self.list_surveys()
        all_responses = {}

        for survey in surveys:
            survey_id = survey['id']
            responses = self.get_responses(
                survey_id, 
                start_date=start_date, 
                end_date=end_date, 
                order=order
            )
            all_responses[survey_id] = responses

        return all_responses

    def get_survey(self, survey_id: str):
        """
        Obtém as questões de uma pesquisa.

        :param survey_id: O ID da pesquisa cujas questões serão recuperadas.
        
        :return: Um dicionário com as questões da pesquisa.
        """
        url = f"https://api.inovyo.com/v2/survey/{survey_id}/questions"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response = requests.get(url, headers=headers)
        while response.status_code == 401 and self.auth:
            self.refresh_token()
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            response = requests.get(url, headers=headers)
        return response.json()




'''
# contacts
def list_contacts(api_client: APIClient):
    """Lista todos os contatos."""
    url = "https://api.inovyo.com/v2/contact/"
    return api_client.make_request('GET', url)

def get_contact_details(api_client: APIClient, contact_id: str):
    """Obtém os detalhes de um contato específico."""
    url = f"https://api.inovyo.com/v2/contact/{contact_id}"
    return api_client.make_request('GET', url)

def get_contact_survey_link(api_client: APIClient, contact_id: str):
    """Obtém o link de pesquisa para um contato específico."""
    url = f"https://api.inovyo.com/v2/contact/survey_link"
    data = {"contact_id": contact_id}
    return api_client.make_request('POST', url, json=data)

def send_batch_contacts(api_client: APIClient, contacts_data: list):
    """Envia um lote de contatos."""
    url = "https://api.inovyo.com/v2/contact/batch"
    return api_client.make_request('POST', url, json=contacts_data)

def set_contact_webhook(api_client: APIClient, webhook_url: str):
    """Configura o webhook de contatos."""
    url = "https://api.inovyo.com/v2/contact/webhook"
    data = {"webhook_url": webhook_url}
    return api_client.make_request('POST', url, json=data)
'''