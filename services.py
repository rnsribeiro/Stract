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

def get_platform_fields(platform_value):
    """Obtém todos os campos de uma plataforma específica, lidando com paginação."""
    fields = []
    page = 1  # Começa na primeira página

    try:
        while True:
            response = requests.get(
                f"{BASE_URL}fields?platform={platform_value}&page={page}", 
                headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
            )
            response.raise_for_status()
            data = response.json()            

            # Adiciona os novos campos, evitando duplicatas
            new_fields = data.get("fields", [])
            for field in new_fields:
                if field not in fields:
                    fields.append(field)

            # Verifica se há mais páginas
            pagination = data.get("pagination", {})
            current_page = pagination.get("current", 1)
            total_pages = pagination.get("total", 1)

            if current_page >= total_pages:
                break  # Sai do loop se todas as páginas foram processadas

            page += 1  # Avança para a próxima página

        #print(f"Campos da plataforma {platform_value}: {fields}")
        return fields

    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar campos da plataforma {platform_value}: {e}")
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

    fields = get_platform_fields(platform_value)
        
    # Criando a string com base nos valores de 'value' dos dicionários em 'fields'
    fields_str = ",".join([field["value"] for field in fields if isinstance(field, dict) and "value" in field])

    try:        

        response = requests.get(
            f"{BASE_URL}insights?platform={platform_value}&account={account_id}&token={account_token}&fields={fields_str}",
            headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
        )
        #print(f"{BASE_URL}insights?platform={platform_value}&account={account_id}&token={account_token}&fields={fields_str}")
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
    
    # Iterando sobre as contas
    for account in accounts:
        account_id = account["id"]
        account_name = account["name"]
        account_token = account["token"]
        
        # Obtendo os insights para a conta
        insights = get_insights_for_account(account_id, account_token, platform_value)

        # Caso não haja insights, cria um dicionário padrão
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
            # Itera sobre os anúncios (insights)
            for ad in insights:
                if not isinstance(ad, dict):
                    print(f"Erro: item inesperado na lista de insights -> {ad}")
                    continue
                
                # Criando um dicionário para armazenar os dados do anúncio
                ad_data = {"account_name": account_name}
                
                # Preenchendo o dicionário com todos os campos presentes nos insights
                for field in ad:
                    ad_data[field] = ad.get(field, "-")  # Se o campo não existir, coloca "-"
                
                all_data.append(ad_data)
        
    return all_data


def get_summary_by_account(platform_value):
    """Gera um resumo colapsando os dados por conta, somando valores numéricos e deixando vazios os campos de texto."""
    
    insights = get_accounts_and_insights(platform_value)
    summary = {}

    for insight in insights:
        account_name = insight["account_name"]

        if account_name not in summary:
            summary[account_name] = {"account_name": account_name}

        for key, value in insight.items():
            if key == "account_name":
                continue  # Já está no sumário

            if isinstance(value, (int, float)) or str(value).replace(".", "", 1).isdigit():
                # Somamos os valores numéricos
                summary[account_name][key] = summary[account_name].get(key, 0) + float(value)
            else:
                # Campos de texto ficam vazios
                summary[account_name][key] = ""

    return list(summary.values())


def get_all_ads_report():
    """Obtém todos os anúncios de todas as plataformas e gera o relatório."""
    all_data = []
    platforms = get_platforms()  # Pega todas as plataformas

    for platform in platforms:
        platform_value = platform["value"]
        platform_name = platform["text"]

        # Obtemos os anúncios dessa plataforma
        ads = get_accounts_and_insights(platform_value)

        # Adiciona as informações de plataforma e conta a cada anúncio
        for ad in ads:
            account_name = ad["account_name"]
            ad_data = {
                "platform_name": platform_name,
                "account_name": account_name,
                "ad_name": ad.get("ad_name", "-"),
                "impressions": ad.get("impressions", "-"),
                "cost": ad.get("cost", "-"),
                "region": ad.get("region", "-"),
                "clicks": ad.get("clicks", "-"),
                "status": ad.get("status", "-"),
                "cost_per_click": "-"
            }
            # Calculando o CPC (Cost per Click) se possível
            if ad.get("cost") not in ["-", None] and ad.get("clicks") not in ["-", None, "0"]:
                ad_data["cost_per_click"] = round(float(ad["cost"]) / float(ad["clicks"]), 2)

            all_data.append(ad_data)

    return all_data

