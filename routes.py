from flask import render_template
from services import (
    get_platforms,
    get_platform_name,
    get_accounts_and_insights,
    get_summary_by_account,
    get_all_ads_report
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
        summary = get_summary_by_account(platform)
        platform_name = get_platform_name(platform)
        return render_template("resumo.html", platform_name=platform_name, platform_value=platform, summary=summary)

    @app.route('/geral')
    def geral_report():
        """Relatório geral com todos os anúncios de todas as plataformas"""
        report_data = get_all_ads_report()

        # A lista de campos do relatório, com exceção de "Cost per Click"
        report_fields = [
            "platform_name", "account_name", "ad_name", "impressions", 
            "cost", "region", "clicks", "status", "cost_per_click"
        ]
        
        return render_template('geral.html', report_data=report_data, report_fields=report_fields)
