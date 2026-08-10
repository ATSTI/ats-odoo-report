# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatórios personalizados para o Caldana',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'ATSTi Soluções',
    'description': """
            Relatorio personalizado para o Caldana
    """,
    'author': 'ATSTi,Odoo Community Association (OCA)',
    'maintainer': 'OtavioAndretta <otavio12257@gmail.com>',
    'website': '',
    'depends': [
        'base','sale','account'
    ],
    'data': [
        'report/report_faturas_inherit.xml',
        'views/account_move.xml'
    ],
    'installable': True,
    'application': False,
}
