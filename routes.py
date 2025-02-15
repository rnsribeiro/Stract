from flask import render_template
from csv_utils import (
    generate_csv_from_insights,
    generate_csv_from_summary,
    generate_csv_from_general_summary
)
from services import (
    get_platforms,
    get_platform_name,
    get_accounts_and_insights,
    get_summary_by_account,
    get_all_ads_report,
    get_general_summary    
)

def register_routes(app):
    """Registra todas as rotas da aplicação."""

    @app.route("/")
    def root():
        """Página inicial"""
        user_data = {
            "name": "Rodrigo Nunes Sampaio Ribeiro",
            "email": "rnsribeiro@gmail.com",
            "linkedin": "https://www.linkedin.com/in/rodrigo-nsribeiro/"
        }
        return render_template("index.html", user_data=user_data)

    @app.route("/plataformas")
    def plataformas():
        """Página que exibe uma tabela com as plataformas disponíveis"""
        platforms = get_platforms()
        return render_template("plataformas.html", platforms=platforms)

    @app.route("/<platform>")
    def show_platform(platform):
        """Exibe insights da plataforma"""
        insights = get_accounts_and_insights(platform)
        platform_name = get_platform_name(platform)
        return render_template("platform.html", platform_name=platform_name, platform_value=platform, insights=insights)

    @app.route("/<platform>/resumo")
    def show_summary(platform):
        """Mostra o resumo da plataforma"""
        summarys = get_summary_by_account(platform)            
        platform_name = get_platform_name(platform)
        return render_template("resumo.html", platform_name=platform_name, platform_value=platform, summarys=summarys)

    @app.route('/geral')
    def geral_report():
        """Relatório geral com todos os anúncios de todas as plataformas"""
        report_data, report_fields = get_all_ads_report()
        return render_template('geral.html', report_data=report_data, report_fields=report_fields)

    @app.route('/geral/resumo')
    def geral_resumo():
        # Supondo que você tenha a função `get_general_summary` que retorna os dados
        dados = get_general_summary()
        return render_template('geral_resumo.html', dados=dados)

    # Rotas para download de CSV
    @app.route("/download/<platform>")
    def download_csv(platform):
        """Download dos dados da plataforma em formato CSV"""
        insights = get_accounts_and_insights(platform)
        return generate_csv_from_insights(insights, platform)

    @app.route("/download/<plaform>/resumo")
    def download_summary_csv(plaform):
        """Download dos dados do resumo da plataforma em formato CSV"""
        summary = get_summary_by_account(plaform)
        return generate_csv_from_summary(summary, plaform)

    @app.route("/download/geral")
    def download_geral_csv():
        """Download dos dados geral em formato CSV"""
        report_data, report_fields = get_all_ads_report()
        return generate_csv_from_insights(report_data, "geral")

    @app.route("/download/geral/resumo")
    def download_geral_resumo_csv():
        # Supondo que você tenha a função `get_general_summary` que retorna os dados
        dados = get_general_summary()
        print(dados)
        return generate_csv_from_general_summary(dados)