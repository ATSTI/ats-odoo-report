# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatórios personalizados para a Fritisco',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'ATSTi Soluções',
    'description': """
            Relatórios personalizados para a Fritisco filtrando por vendedores específicos, parcelas, produtos e datas iniciais/finais
    """,
    'author': 'ATSTi,Odoo Community Association (OCA)',
    'maintainer': 'OtavioAndretta <otavio12257@gmail.com>',
    'website': '',
    'depends': [
        'l10n_br_sale','base','sale','account','product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'view/comissao_wizard_view.xml',
        'report/report_comissao_template.xml',
        'report/report_pedido_venda_faturas.xml',
        'view/vendas_wizard_view.xml',
        'report/report_vendas_template.xml',
    ],
    'installable': True,
    'application': False,
}
