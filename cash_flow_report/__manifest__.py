# Author: Carlos Silveira
# Copyright 2022 ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Cash Flow Reports",
    "version": "16.0",
    "category": "Reporting",
    "summary": "Financial Reports",
    "author": "ATSTi Soluções",
    "website": "",
    "depends": ["web", "account", "date_range", "report_xlsx", "account_payment_partner"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/cash_flow_wizard_view.xml",
        "menuitems.xml",
        "reports.xml",
        "report/templates/layouts.xml",
        "report/templates/cash_flow.xml",
        "view/report_cash_flow.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "cash_flow_report/static/src/js/action_manager_report.js",
            "cash_flow_report/static/src/js/client_action.js",
            "cash_flow_report/static/src/xml/report.xml",
        ],
        "web.report_assets_common": [
            "cash_flow_report/static/src/js/report.js",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
}