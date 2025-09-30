# Weni Example Agents

Este repositório contém exemplos de agentes inteligentes desenvolvidos para a plataforma Weni CLI. Cada agente é especializado em uma funcionalidade específica e utiliza diferentes APIs externas para fornecer informações relevantes aos usuários.

## 📚 Agentes Disponíveis

### 1. Book Agent (Agente de Livros)
**Localização:** `books/`

**Funcionalidade:** Especialista em buscar informações detalhadas sobre livros utilizando a Google Books API.

**Características:**
- Busca livros por título
- Traduz automaticamente descrições do inglês para português brasileiro
- Fornece informações completas: autores, editora, data de publicação, número de páginas, avaliações
- Sugere títulos similares quando não encontra o livro específico
- Retorna até 5 resultados por busca

**Ferramenta:**
- `get_books`: Busca informações de livros na Google Books API

**Parâmetros:**
- `book_title` (obrigatório): Título do livro a ser pesquisado

**Exemplo de uso:**
```bash
weni run agent_definition.yaml book_agent get_books -v
```

---

### 2. Movie Agent (Agente de Filmes)
**Localização:** `movies/`

**Funcionalidade:** Especialista em buscar informações detalhadas sobre filmes utilizando a The Movie Database (TMDB) API.

**Características:**
- Busca filmes por título (traduz automaticamente do português para inglês)
- Traduz sinopses do inglês para português brasileiro
- Mantém títulos originais em inglês com traduções informais entre parênteses
- Fornece informações: título, sinopse, data de lançamento, avaliação, imagens
- Sugere títulos similares quando não encontra o filme específico
- Retorna até 5 resultados por busca

**Ferramenta:**
- `get_movies_new`: Busca informações de filmes na TMDB API

**Parâmetros:**
- `movie_title` (obrigatório): Título do filme a ser pesquisado

**Credenciais necessárias:**
- `movies_api_key`: Chave da API do The Movie Database

**Exemplo de uso:**
```bash
weni run agent_definition.yaml movie_agent get_movies_new -v
```

---

### 3. News Agent (Agente de Notícias)
**Localização:** `news/`

**Funcionalidade:** Especialista em buscar e fornecer notícias atualizadas sobre qualquer tópico utilizando a NewsAPI.

**Características:**
- Busca notícias por tópico específico
- Fornece contexto breve sobre as notícias encontradas
- Sugere tópicos relacionados quando não encontra notícias
- Mantém tom profissional e imparcial
- Retorna até 10 artigos por busca
- Responde sempre em inglês

**Ferramenta:**
- `get_news`: Busca notícias na NewsAPI

**Parâmetros:**
- `topic` (obrigatório): Tópico sobre o qual buscar notícias

**Credenciais necessárias:**
- `apiKey`: Chave da API do NewsAPI

**Exemplo de uso:**
```bash
weni run agent_definition.yaml news_agent get_news
```

---

### 4. Orders Management Agent (Agente de Gerenciamento de Pedidos)
**Localização:** `sheets/`

**Funcionalidade:** Especialista em gerenciar pedidos de restaurante através de planilhas Google Sheets.

**Características:**
- **Registrar Pedidos:** Registra novos pedidos com data/hora automática (horário de Brasília)
- **Consultar Pedidos:** Busca pedidos específicos por ID ou lista todos os pedidos
- **Consultar Cardápio:** Mostra pratos disponíveis diretamente da planilha
- **Listar Pedidos:** Organiza e exibe todos os pedidos registrados
- Gera IDs únicos e status aleatórios automaticamente
- Trabalha com planilha Google Sheets específica

**Ferramentas:**
- `get_order_data`: Consulta pedidos por ID ou lista todos
- `insert_order_data`: Registra novo pedido na planilha
- `get_menu_data`: Consulta cardápio por categoria ou busca específica

**Parâmetros:**
- `get_order_data`:
  - `order_id` (opcional): ID do pedido para busca específica
- `insert_order_data`:
  - `prato` (obrigatório): Nome do prato pedido
  - `cliente` (obrigatório): Nome do cliente
- `get_menu_data`:
  - `categoria` (opcional): Categoria específica (hamburguer, pizza, massas, etc.)
  - `busca` (opcional): Termo para buscar pratos por nome ou descrição

**Credenciais necessárias:**
- Arquivo `credentials.json` para autenticação com Google Sheets

**Exemplo de uso:**
```bash
weni run agent_definition.yaml orders_manager get_order_data -v
weni run agent_definition.yaml orders_manager insert_order_data -v 
weni run agent_definition.yaml orders_manager get_menu_data -v
```

---

## 🚀 Como Usar

### Pré-requisitos
- Python instalado na máquina

### Instalação
```bash
pip install weni-cli
```

### Autenticação
```bash
weni login
```

### Seleção do Projeto
```bash
weni project list
weni project use UUID_DO_PROJETO
```

### Execução dos Agentes

#### Book Agent
```bash
cd books
weni run agent_definition.yaml book_agent get_books
```

#### Movie Agent
```bash
cd movies
weni run agent_definition.yaml movie_agent get_movies_new
```

#### News Agent
```bash
cd news
weni run agent_definition.yaml news_agent get_news
```

#### Orders Management Agent
```bash
cd sheets
weni run agent_definition.yaml orders_manager get_order_data
```

### Upload dos Agentes
Após testar, faça o upload do agente:
```bash
weni project push agent_definition.yaml
```

## 🔄 Diferença entre `weni run` e `weni project push`

### `weni run` - Validação Local
- **Propósito:** Validar a execução do código Python/ferramenta localmente
- **Funcionamento:** Executa apenas a ferramenta específica sem contexto conversacional
- **Uso:** Testar se o código está funcionando corretamente antes do upload
- **Exemplo:**
```bash
weni run agent_definition.yaml book_agent get_books -v
```

### `weni project push` - Upload para Produção
- **Propósito:** Fazer upload do agente completo para um projeto na plataforma Weni
- **Funcionamento:** Envia toda a configuração do agente (instruções, guardrails, ferramentas) para a Weni
- **Uso:** Deploy do agente para permitir testes conversacionais reais
- **Resultado:** Após o upload, o agente estará disponível para interação conversacional no projeto Weni
- **Exemplo:**
```bash
weni project push agent_definition.yaml
```

### Fluxo Recomendado
1. **Desenvolvimento:** Crie e configure o agente
2. **Validação:** Use `weni run` para testar as ferramentas individualmente
3. **Upload:** Use `weni project push` para enviar o agente para a Weni
4. **Teste Conversacional:** Teste o agente completo na interface da Weni

## 📋 Estrutura do Projeto

```
weni-example-agents/
├── books/                    # Agente de livros
│   ├── agent_definition.yaml
│   └── tools/
│       └── get_books/
│           ├── books.py
│           ├── requirements.txt
│           └── test_definition.yaml
├── movies/                   # Agente de filmes
│   ├── agent_definition.yaml
│   └── tools/
│       └── get_movies/
│           ├── main.py
│           ├── requirements.txt
│           └── test_definition.yaml
├── news/                     # Agente de notícias
│   ├── agent_definition.yaml
│   └── tools/
│       └── get_news/
│           ├── main.py
│           ├── requirements.txt
│           └── test_definition.yaml
└── sheets/                   # Agente de planilhas
    ├── agent_definition.yaml
    └── tools/
        ├── get_data/         # Consultar pedidos
        ├── insert_data/      # Inserir pedidos
        └── menu_data/        # Consultar cardápio
```

## 🔧 Configuração de Credenciais

### APIs Externas
- **Google Books API:** Não requer chave (gratuita)
- **TMDB API:** Requer chave de API do The Movie Database
- **NewsAPI:** Requer chave de API do NewsAPI

### Google Sheets
- Requer arquivo `credentials.json` para autenticação
- Deve ter permissões de leitura/escrita na planilha específica

## 📝 Notas Importantes

1. **Tradução Automática:** Os agentes de livros e filmes traduzem automaticamente as descrições para português brasileiro
2. **Horário de Brasília:** O agente de pedidos usa automaticamente o horário de Brasília
3. **IDs Únicos:** O agente de pedidos gera IDs sequenciais únicos automaticamente
4. **Status Aleatórios:** Os pedidos recebem status aleatórios (Pronto, Em Preparação, Entregue)
5. **Limites de Resultados:** Cada agente tem limites específicos de resultados para otimizar performance

## 🤝 Contribuição

Para contribuir com este projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Implemente suas alterações
4. Teste os agentes
5. Envie um pull request
