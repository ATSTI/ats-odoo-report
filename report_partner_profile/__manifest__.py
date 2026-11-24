# -*- coding: utf-8 -*-

{
    'name': 'Relatorio De Ficha Cadastral',
    'version': '1.0',
    'category': 'Partners',
    'sequence': 2,
    'summary': 'relatorios personalizados',
    'description': """ Relatorio customizado para visualização de dados do parceiro
    """,
    'author': 'ATSTi Solucoes',
    'website': 'http://www.atsti.com.br',
    'contributors': [
        'Mauricio Silveira <mauriciors320@gmail.com>',
        'Otavio Andretta <otavio12257@gmail.com>'
    ],
    'depends': ['l10n_br_base'],
    'data': [
        'report/report_actions.xml',
        'report/report_partner_profile.xml',
    ],
    'installable': True,
    'application': False,
}
