from flask import Flask, render_template
from collections import defaultdict
import requests
import os

app = Flask(__name__)

BASE_URL = os.getenv("URL")
BEARER_TOKEN = os.getenv("API_TOKEN") 

def get_platforms():
    """Obtém a lista de plataformas disponíveis."""
    try:
        response = requests.get(f"{BASE_URL}platforms", headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        response.raise_for_status()
        return response.json().get("platforms", [])
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar plataformas: {e}")
        return []

def get_platform_name(platform_value):
    """Retorna o nome da plataforma com base no platform_value."""
    platforms = get_platforms()
    
    for platform in platforms:
        if platform.get("value") == platform_value:
            return platform.get("text", platform_value)  # Retorna o nome da plataforma ou o próprio valor se não encontrado
    return platform_value  # Se não encontrar, retorna o próprio valor

def get_accounts(platform_value):
    """Obtém todas as contas de uma plataforma específica, incluindo várias páginas de resultados."""
    all_accounts = []
    page = 1
    
    while True:
        try:
            # Fazendo a requisição para a API da plataforma com base na página atual
            response = requests.get(f"{BASE_URL}accounts?platform={platform_value}&page={page}", 
                                    headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
            response.raise_for_status()  # Lança um erro se a resposta for inválida

            data = response.json()
            accounts = data.get("accounts", [])
            all_accounts.extend(accounts)  # Adiciona as contas dessa página à lista

            # Verifica se há mais páginas
            pagination = data.get("pagination", {})
            # Se a chave 'pagination' não existir ou se os valores 'current' e 'total' não existirem, sai do loop
            if not pagination.get("current") or not pagination.get("total") or pagination.get("current") >= pagination.get("total"):
                break  # Se não houver mais páginas ou não houver paginação, sai do loop
            else:
                page += 1

        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar contas para a plataforma {platform_value}: {e}")
            break

    return all_accounts


def get_insights_for_account(account_id, account_token, platform_value):
    """Obtém os anúncios de uma conta específica."""

    all_insights = []

    try:
        response = requests.get(
            f"{BASE_URL}insights?platform={ platform_value }&account={ account_id }&token={ account_token }&fields=adName,impressions,cost,region,clicks,status",
            headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
        )
        response.raise_for_status()  # Lança um erro se a resposta for inválida
        data = response.json()
        insights = data.get("insights", [])
        all_insights.extend(insights)

        # Garante que o retorno seja uma lista extraindo a chave "insights"
        return all_insights

    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar insights da conta de id {account_id}: {e}")
        return []

def get_accounts_and_insights(platform_value):
    """Combina as contas da plataforma com seus anúncios."""
    all_data = []
    accounts = get_accounts(platform_value)

    
    for account in accounts:
        account_id = account["id"]
        account_name = account["name"]
        account_token = account["token"]

        # Obtém os anúncios da conta
        insights = get_insights_for_account(account_id, account_token, platform_value)        

        # Se não houver anúncios, adiciona uma linha indicando isso
        if not insights:
            all_data.append({
                "account_name": account_name,
                "ad_name": "Sem anúncios",
                "impressions": "-",
                "cost": "-",
                "region": "-",
                "clicks": "-",
                "status": "-"
            })
        else:
            for ad in insights:
                if not isinstance(ad, dict):  
                    print(f"Erro: item inesperado na lista de insights -> {ad}")  
                    continue  # Pula itens que não sejam dicionários

                all_data.append({
                    "account_name": account_name,
                    "ad_name": ad.get("adName", "-"),
                    "impressions": ad.get("impressions", "-"),
                    "cost": ad.get("cost", "-"),
                    "region": ad.get("region", "-"),
                    "clicks": ad.get("clicks", "-"),
                    "status": ad.get("status", "-")
                })

    return all_data

def get_summary_by_account(platform_value):
    """Gera um resumo somando apenas os cliques por conta."""
    insights = get_accounts_and_insights(platform_value)
    summary = {}

    for insight in insights:
        account_name = insight["account_name"]

        if account_name not in summary:
            summary[account_name] = {
                "account_name": account_name,
                "impressions": 0,
                "cost": 0.0,
                "clicks": 0  
            }

        summary[account_name]["impressions"] += int(str(insight["impressions"])) if str(insight["impressions"]).isdigit() else 0        
        summary[account_name]["clicks"] += int(str(insight["clicks"])) if str(insight["clicks"]).isdigit() else 0

        if insight["cost"] != "-":
            summary[account_name]["cost"] += float(insight["cost"])

    resultado = list(summary.values())    

    return resultado



@app.route('/')
def root():
    """Página inicial com informações pessoais e menu"""
    user_data = {
        "name": "Rodrigo Nunes Sampaio Ribeiro",
        "email": "rnsribeiro@gmail.com",
        "linkedin": "https://www.linkedin.com/in/rodrigo-nsribeiro/"
    }
    return render_template('index.html', user_data=user_data)

@app.route('/plataformas')
def plataformas():
    """Página que exibe uma tabela com as plataformas disponíveis"""
    platforms = get_platforms()  
    return render_template('plataformas.html', platforms=platforms)

@app.route("/<platform>")
def show_platform(platform):
    insights = get_accounts_and_insights(platform)
    platform_name = get_platform_name(platform)
    return render_template("platform.html", platform_name=platform_name, platform_value=platform, insights=insights)

@app.route("/<platform>/resumo")
def show_summary(platform):
    summary = get_summary_by_account(platform)
    platform_name = get_platform_name(platform)
    return render_template("resumo.html", platform_name=platform_name, platform_value=platform, summary=summary)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Mudança para 5000 se porta 80 exigir permissão de root
    app.run(host="0.0.0.0", port=port, debug=True)
