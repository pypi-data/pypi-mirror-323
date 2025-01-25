# Inovyo API

Biblioteca para integração com as APIs da Inovyo.

## Instalação

Para instalar a biblioteca, você pode usar o pip:

```bash
pip install inovyo-api
```

## Configuração das Credenciais

Para utilizar a API, você precisa definir suas credenciais de autenticação. Você pode fazer isso de duas maneiras: passando as credenciais diretamente ao inicializar o cliente ou definindo variáveis de ambiente.

### 1. Definindo Variáveis de Ambiente

#### No macOS e Linux

Se você estiver usando o shell Bash ou Zsh, adicione as seguintes linhas ao seu arquivo de configuração do shell (`~/.bashrc`, `~/.bash_profile` ou `~/.zshrc`):

```bash
export INOVYO_KEY="seu_token_aqui"
export INOVYO_SECRET="seu_segredo_aqui"
```

Depois, recarregue o arquivo de configuração:

```bash
source ~/.bashrc
```
ou
```bash
source ~/.zshrc
```

#### No Windows

Você pode definir as variáveis de ambiente através do Painel de Controle ou usando o PowerShell.

**Usando o Painel de Controle**:
1. Abra o Painel de Controle.
2. Vá para Sistema e Segurança > Sistema > Configurações avançadas do sistema.
3. Clique em "Variáveis de Ambiente".
4. Na seção "Variáveis do sistema", clique em "Nova" e adicione:
   - Nome da variável: `INOVYO_KEY`
   - Valor da variável: `seu_token_aqui`
   
   E depois adicione outra:
   - Nome da variável: `INOVYO_SECRET`
   - Valor da variável: `seu_segredo_aqui`

**Usando o PowerShell**:
1. Abra o PowerShell.
2. Defina as variáveis de ambiente:

```powershell
[System.Environment]::SetEnvironmentVariable("INOVYO_KEY", "seu_token_aqui", "User")
[System.Environment]::SetEnvironmentVariable("INOVYO_SECRET", "seu_segredo_aqui", "User")
```

### 2. Passando Credenciais Diretamente

Alternativamente, você pode passar as credenciais diretamente ao inicializar o cliente da API:

```python
from api_inovyo import InovyoAPIClient
```

## Uso

Aqui você pode adicionar exemplos de como usar a biblioteca. Por exemplo, para listar pesquisas disponíveis:

```python
from api_inovyo import InovyoAPIClient

# Inicializa o cliente da API com as credenciais
client = InovyoAPIClient(api_token="seu_token_aqui", api_secret="seu_segredo_aqui")

# Teste uma chamada de API, como listar pesquisas
try:
    surveys = client.list_surveys()
    print("Pesquisas disponíveis:", surveys)
except Exception as e:
    print("Erro ao acessar a API:", e)
```