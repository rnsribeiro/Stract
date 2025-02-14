import requests
import os

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
            return platform.get("text", platform_value)
    return platform_value

def get_accounts(platform_value):
    """Obtém todas as contas de uma plataforma específica."""
    all_accounts = []
    page = 1
    while True:
        try:
            response = requests.get(
                f"{BASE_URL}accounts?platform={platform_value}&page={page}",
                headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
            )
            response.raise_for_status()
            data = response.json()
            accounts = data.get("accounts", [])
            all_accounts.extend(accounts)
            pagination = data.get("pagination", {})
            if not pagination.get("current") or not pagination.get("total") or pagination["current"] >= pagination["total"]:
                break
            else:
                page += 1
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar contas para a plataforma {platform_value}: {e}")
            break
    return all_accounts

def get_insights_for_account(account_id, account_token, platform_value):
    """Obtém os insights de uma conta específica."""
    try:
        response = requests.get(
            f"{BASE_URL}insights?platform={platform_value}&account={account_id}&token={account_token}&fields=adName,impressions,cost,region,clicks,status",
            headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("insights", [])
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar insights da conta de id {account_id}: {e}")
        return []

def get_accounts_and_insights(platform_value):
    """Combina contas com seus insights."""
    all_data = []
    accounts = get_accounts(platform_value)
    for account in accounts:
        account_id = account["id"]
        account_name = account["name"]
        account_token = account["token"]
        insights = get_insights_for_account(account_id, account_token, platform_value)

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
                    continue
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

    return list(summary.values())
