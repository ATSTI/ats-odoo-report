# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request

class DREController(http.Controller):

    @http.route('/ats_dre_report/open_lines', type='http', auth='user')
    def open_lines(self, company_id=None, account_id=None, date_from=None, date_to=None, posted='1', **kw):
        """
        Abre a lista de account.move.line já filtrada por empresa, conta e período.
        Gera uma página mínima com JS que navega para /web#... preservando o 'context'
        (evita perda do fragmento/hash em redirecionamentos e garante breadcrumb).
        """
        # action conforme "postados" ou "todos"
        xmlid = 'ats_dre_report.action_open_move_lines_posted' if posted == '1' else 'ats_dre_report.action_open_move_lines_all'
        action_id = request.env.ref(xmlid).id

        # breadcrumb (menu Contabilidade/Relatórios)
        menu = request.env.ref('account.menu_finance_reports', raise_if_not_found=False)
        menu_id = menu.id if menu else ''

        ctx = {
            "ctx_company_id": int(company_id or 0),
            "ctx_account_id": int(account_id or 0),
            "ctx_date_from": date_from,
            "ctx_date_to": date_to,
        }
        # Monta a página com JS criando a URL final (context em JSON + encodeURIComponent)
        # Usamos window.location.replace para não poluir o histórico.
        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Abrindo Lançamentos…</title></head>
<body>
<script>
  (function () {{
    var ctx = {json.dumps(ctx)};
    var url = '/web#action={action_id}&model=account.move.line&view_type=list&cids={company_id or ""}&menu_id={menu_id}&context='
            + encodeURIComponent(JSON.stringify(ctx));
    window.location.replace(url);
  }})();
</script>
</body></html>"""
        return html
