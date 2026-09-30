from flask import Blueprint, render_template

from app.security import requer_financeiro
from app.services.atendimento_service import atendimento_service
from app.services.dashboard_service import dashboard_service

bp = Blueprint("dashboard", __name__)


@bp.get("/")
@requer_financeiro
def dashboard():
    dash = dashboard_service.get_dashboard()
    atendimentos = [
        a
        for a in atendimento_service.listar_por_status("EM_ANDAMENTO")
    ][:5]
    return render_template(
        "dashboard.html",
        dash=dash,
        atendimentos=atendimentos,
        pageTitle="Dashboard",
        activePage="dashboard",
    )