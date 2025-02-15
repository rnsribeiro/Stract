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
    page = 1  

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
    platforms = get_platforms()
    all_fields = set(["account_name", "cost_per_click"])

    # Mapeamento de campos similares para um único nome padrão
    field_mapping = {
        "adname": "ad_name",
        "ad name": "ad_name",
        "cpc": "cost_per_click",
        "spend": "cost",  # Unificando "spend" e "cost"
        "effective_status": "status",  # Unificando "effective_status" e "status"
        "country": "region"  # Unificando "country" e "region"
    }

    for platform in platforms:
        platform_value = platform["value"]
        platform_name = platform["text"]

        ads = get_accounts_and_insights(platform_value)

        for ad in ads:
            account_name = ad.get("account_name", "-")
            ad_data = {
                "platform_name": platform_name,
                "account_name": account_name
            }

            has_cost_per_click = False  # Flag para verificar se a API já fornece CPC

            for key, value in ad.items():
                if key == "id":  # Ignora a coluna "id"
                    continue
                
                normalized_key = field_mapping.get(key.lower(), key)  # Normaliza o nome do campo
                ad_data[normalized_key] = value if value not in ["-", None] else "-"

                if normalized_key == "cost_per_click" and value not in ["-", None]:
                    has_cost_per_click = True  # A API já fornece CPC, não calculamos manualmente

                all_fields.add(normalized_key)  # Adiciona o campo na lista global

            # Mescla os campos "spend" e "cost", priorizando "spend"
            if "spend" in ad and ad["spend"] not in ["-", None]:
                ad_data["cost"] = ad["spend"]
            elif "cost" in ad and ad["cost"] not in ["-", None]:
                ad_data["cost"] = ad["cost"]
            else:
                ad_data["cost"] = "-"

            # Mescla os campos "effective_status" e "status", priorizando "effective_status"
            if "effective_status" in ad and ad["effective_status"] not in ["-", None]:
                ad_data["status"] = ad["effective_status"]
            elif "status" in ad and ad["status"] not in ["-", None]:
                ad_data["status"] = ad["status"]
            else:
                ad_data["status"] = "-"

            # Mescla "country" e "region", priorizando "country"
            if "country" in ad and ad["country"] not in ["-", None]:
                ad_data["region"] = ad["country"]
            elif "region" in ad and ad["region"] not in ["-", None]:
                ad_data["region"] = ad["region"]
            else:
                ad_data["region"] = "-"

            # Cálculo do CPC (Cost per Click) apenas se não existir "cost_per_click" ou "cpc"
            if not has_cost_per_click:
                if ad_data["cost"] not in ["-", None] and ad.get("clicks") not in ["-", None, "0"]:
                    try:
                        ad_data["cost_per_click"] = round(float(ad_data["cost"]) / float(ad["clicks"]), 2)
                    except ValueError:
                        ad_data["cost_per_click"] = "-"

            all_data.append(ad_data)

    # Define a ordem das colunas, garantindo que "platform_name" e "account_name" venham primeiro
    ordered_fields = ["platform_name", "account_name"] + sorted(field for field in all_fields if field not in ["platform_name", "account_name"])

    return all_data, ordered_fields

def get_general_summary():
    """Gera um resumo geral agregando os dados por plataforma e somando valores numéricos, omitindo o campo 'cpc'."""
    platforms = get_platforms()
    summary = {}

    for platform in platforms:
        platform_value = platform["value"]
        platform_name = platform["text"]

        # Obtendo os dados dos anúncios
        ads = get_accounts_and_insights(platform_value)

        for ad in ads:
            # Agrupando os dados por plataforma
            if platform_name not in summary:
                summary[platform_name] = {"platform_name": platform_name}

            for key, value in ad.items():
                # Omitindo o campo 'cpc'
                if key == "platform_name" or key == "cpc":
                    continue  # Ignora o campo 'cpc'
                
                # Somando os valores numéricos
                if isinstance(value, (int, float)) or str(value).replace(".", "", 1).isdigit():
                    summary[platform_name][key] = summary[platform_name].get(key, 0) + float(value)
                else:
                    # Mantendo os campos de texto vazios
                    summary[platform_name][key] = ""
 
    # Transformando o resumo em uma lista para fácil manipulação no template
    return list(summary.values())