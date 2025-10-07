# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountAccount(models.Model):
    _inherit = 'account.account'

    dre_section = fields.Selection([
        ('rev_gross', 'Receita Bruta'),
        ('rev_deductions', 'Deduções de Receita'),
        ('rev_net', 'Receita Líquida'),
        ('cogs', 'Custo Direto / COGS'),
        ('opex', 'Despesas Operacionais'),
        ('fin_income', 'Receitas Financeiras'),
        ('fin_expense', 'Despesas Financeiras'),
        ('other_income', 'Outras Receitas'),
        ('other_expense', 'Outras Despesas'),
        ('tax_income', 'IR/CSLL'),
    ], string='Seção DRE', help='Classificação opcional para o relatório DRE.')

    @api.onchange('account_type')
    def _onchange_account_type_guess_dre(self):
        for rec in self:
            if rec.dre_section:
                continue
            t = rec.account_type
            guess = False
            if t in ('income', 'other_income'):
                guess = 'rev_gross'
            elif t in ('direct_cost',):
                guess = 'cogs'
            elif t in ('expense',):
                guess = 'opex'
            rec.dre_section = guess
