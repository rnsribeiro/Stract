# API de Relatórios de Anúncios

## Sobre

Autor: Rodrigo Nunes Sampaio Ribeiro

## Descrição

Esta é uma aplicação Flask que consome dados de uma API externa de anúncios e gera relatórios em formato CSV.

## Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/rnsribeiro/Stract.git
cd Stract
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente com o arquivo `.env` na raiz do projeto, seguindo o exemplo:
```bash
URL=https://sidebar.stract.to/api/
API_TOKEN=TokenDeAcessoAqui
```

## Executando a aplicação

1. Execute o servidor Flask:
```bash
python app.py
```

2. O servidor estará disponível em [http://localhost:5000](http://localhost:5000)


3. Uma versão do servidor já em funcionamento pode ser acessado através do link [https://stract.onrender.com](https://stract.onrender.com)


## Endpoints disponíveis

- `/` - Retorna informações pessoais
- `/<plataforma>` - Relatório detalhado por plataforma
- `/<plataforma>/resumo` - Relatório resumido por plataforma
- `/geral` - Relatório geral de todas as plataformas
- `/geral/resumo` - Relatório geral resumido por plataforma

## Notas importantes

- Certifique-se de que o token de API está configurado corretamente
- Todos os relatórios são gerados em formato CSV
- Os relatórios incluem cálculo automático de CPC quando necessário
- A aplicação trata dados paginados automaticamente

## Estrutura do código

- `app.py` - Arquivo principal da aplicação Flask que configura o servidor e registra as rotas
- `routes.py` - Gerenciamento de rotas e endpoints da aplicação
  - Rotas para visualização de dados (/plataformas, /`<platform>`, /`<platform>`/resumo, /geral, /geral/resumo)
  - Rotas para download de relatórios CSV
  - Integração entre camadas de serviço e templates
- `services.py` - Serviços de integração com a API e processamento de dados
  - Busca de plataformas e suas configurações
  - Obtenção de contas e insights
  - Normalização e agregação de dados
  - Cálculos de métricas derivadas (CPC, CTR)
- `csv_utils.py` - Utilitários para geração de arquivos CSV
  - Geração de relatórios detalhados por plataforma
  - Geração de relatórios resumidos
  - Normalização de campos para formato CSV
  - Tratamento de headers e formatação de dados
  
 A aplicação utiliza templates HTML renderizados dinamicamente com Flask, além de um arquivo CSS externo para manter a consistência visual.

- `templates/` - Diretório contendo os arquivos HTML utilizados na aplicação
  - `index.html` - Página inicial, apresentando informações pessoais e links para outras páginas
  - `plataformas.html` - Página com uma tabela de plataformas disponíveis na API
  - `platform.html` - Página de detalhes de uma plataforma, contendo uma tabela dinâmica baseada nos dados extraídos
  - `resumo.html` - Página de resumo de anúncios para uma plataforma específica, com estrutura semelhante ao relatório geral
  - `geral.html` - Página do relatório geral de anúncios, contendo uma tabela dinâmica baseada nos dados extraídos  
  - `geral_resumo.html` - Relatório combinado com os dados gerais e resumo consolidado
  - Todos os templates utilizam `Jinja2` para renderizar dinamicamente os dados da aplicação

- `static/` - Diretório para arquivos estáticos (CSS, JS, imagens)
  - `styles.css` - Arquivo centralizado de estilos utilizado em todos os templates
    - Definição de estilos globais para navegação, tabelas e botões de download
    - Layout responsivo com espaçamento e alinhamento adequado dos elementos
    - Estilização das tabelas para exibição clara dos dados (bordas, cores de fundo e realce de cabeçalhos)
