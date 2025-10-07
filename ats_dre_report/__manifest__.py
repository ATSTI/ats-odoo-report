# -*- coding: utf-8 -*-
{
    "name": "ATS DRE Report",
    "summary": "Demonstração do Resultado (DRE) – relatório genérico por tipo de conta",
    "version": "16.0.1.1.1",
    "author": "ATS-TI Soluções, OCA",
    "license": "AGPL-3",
    "website": "https://atsti.com.br",
    "category": "Accounting/Reporting",
    "depends": ["account"],  # <- tiramos "report_xlsx" para não quebrar
    "data": [
        "security/ir.model.access.csv",
        "data/dre_paperformat.xml",
        "views/dre_wizard_views.xml",
        "report/dre_qweb_templates.xml",
        "report/dre_xlsx.xml",          # pode permanecer; o botão vai bloquear se faltar o engine
        "data/dre_menus_actions.xml"
    ],
    "application": False,
    "installable": True
}
