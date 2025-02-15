import csv
from io import StringIO
from flask import make_response

# Funções para o CSV
def generate_csv_from_insights(insights, platform_name):
    """
    Gera um arquivo CSV a partir dos dados de insights.
    
    Args:
        insights (list): Lista de dicionários contendo os dados dos insights
        platform_name (str): Nome da plataforma para definir o nome do arquivo
        
    Returns:
        Response: Objeto response do Flask contendo o arquivo CSV
    """
    if not insights:
        return make_response("No data available", 404)
    
    # Cria um buffer na memória para escrever o CSV
    si = StringIO()
    # Pega as chaves do primeiro insight para usar como cabeçalho, excluindo 'id'
    fieldnames = [key for key in insights[0].keys() if key != 'id']
    writer = csv.DictWriter(si, fieldnames=fieldnames)
    
    # Escreve o cabeçalho
    writer.writeheader()
    
    # Escreve os dados
    for insight in insights:
        # Remove o campo 'id' antes de escrever
        row = {k: v for k, v in insight.items() if k != 'id'}
        writer.writerow(row)
    
    # Prepara a resposta
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={platform_name.replace(' ', '_')}.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output

def generate_csv_from_summary(summary, platform_name):
    """
    Gera um arquivo CSV a partir dos dados de resumo.
    
    Args:
        summary (list): Lista de dicionários contendo os dados de resumo
        platform_name (str): Nome da plataforma para usar como parte do nome do arquivo
        
    Returns:
        Response: Objeto response do Flask contendo o arquivo CSV
    """
    if not summary:
        return make_response("No data available", 404)
    
    # Cria um buffer na memória para escrever o CSV
    si = StringIO()
    # Pega as chaves do primeiro insight para usar como cabeçalho, excluindo 'id'
    fieldnames = [key for key in summary[0].keys() if key != 'id']
    writer = csv.DictWriter(si, fieldnames=fieldnames)
    
    # Escreve o cabeçalho
    writer.writeheader()
    
    # Escreve os dados
    for insight in summary:
        # Remove o campo 'id' antes de escrever
        row = {k: v for k, v in insight.items() if k != 'id'}
        writer.writerow(row)
    
    # Prepara a resposta
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={platform_name.replace(' ', '_')}Resumo.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output

def generate_csv_from_general_summary(summary):
    """
    Gera um arquivo CSV a partir dos dados de resumo geral.
    
    Args:
        summary (list): Lista de dicionários contendo os dados de resumo geral
        
    Returns:
        Response: Objeto response do Flask contendo o arquivo CSV
    """
    if not summary:
        return make_response("No data available", 404)
    
    # Coleta todas as chaves únicas de todos os dicionários
    all_keys = set()
    for item in summary:
        all_keys.update(item.keys())
    
    # Remove 'id' se presente
    if 'id' in all_keys:
        all_keys.remove('id')
    
    # Mapeamento de campos para normalização
    field_mapping = {
        'adname': 'ad_name',
        'ad name': 'ad_name',
        'adName': 'ad_name',
        'spend': 'cost',
        'effective_status': 'status',
        'country': 'region'
    }
    
    # Normaliza as chaves
    normalized_keys = []
    for key in all_keys:
        normalized_key = field_mapping.get(key.lower(), key)
        normalized_keys.append(normalized_key)
    
    # Remove duplicatas mantendo a ordem
    fieldnames = list(dict.fromkeys(normalized_keys))
    
    # Garante que 'platform_name' seja a primeira coluna
    if 'platform_name' in fieldnames:
        fieldnames.remove('platform_name')
        fieldnames = ['platform_name'] + fieldnames
    
    # Cria um buffer na memória para escrever o CSV
    si = StringIO()
    writer = csv.DictWriter(si, fieldnames=fieldnames)
    
    # Escreve o cabeçalho
    writer.writeheader()
    
    # Escreve os dados normalizados
    for item in summary:
        normalized_row = {}
        for key, value in item.items():
            if key != 'id':
                normalized_key = field_mapping.get(key.lower(), key)
                normalized_row[normalized_key] = value
        writer.writerow(normalized_row)
    
    # Prepara a resposta
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=GeralResumo.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output