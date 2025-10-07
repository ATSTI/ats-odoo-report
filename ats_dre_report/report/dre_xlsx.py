# -*- coding: utf-8 -*-
from odoo import models

# Tentamos importar a base do OCA report_xlsx.
# Se o código do módulo não estiver no addons_path, o import falha e criamos um stub.
try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx  # noqa: F401
    HAS_REPORT_XLSX = True
except Exception:
    HAS_REPORT_XLSX = False

if HAS_REPORT_XLSX:
    class ReportDREXlsx(models.AbstractModel):
        _name = 'report.ats_dre_report.report_dre_xlsx'
        _inherit = 'report.report_xlsx'
        _description = 'DRE XLSX Export'

        def generate_xlsx_report(self, workbook, data, wizards):
            # formatos
            fmt_title = workbook.add_format({'bold': True, 'font_size': 12})
            fmt_hdr = workbook.add_format({'bold': True, 'bg_color': '#F2F2F2', 'border': 1})
            fmt_num = workbook.add_format({'num_format': '#,##0.00'})
            fmt_num_neg = workbook.add_format({'num_format': '#,##0.00', 'font_color': '#C0392B'})
            fmt_pct = workbook.add_format({'num_format': '0.00%'})

            for wiz in wizards:
                vals = wiz.get_data()
                cmp = vals.get('comp', {})
                dlt = vals.get('delta', {})
                dpc = vals.get('delta_pct', {})
                add_compare = vals.get('add_compare', False)
                bd = vals.get('breakdown', {})

                # Aba Resumo
                sheet = workbook.add_worksheet('Resumo')
                row = 0
                sheet.write(row, 0, f"DRE - {wiz.company_id.name}", fmt_title); row += 1
                sheet.write(row, 0, f"Período: {wiz.date_from} a {wiz.date_to}"); row += 2

                headers = ['Seção']
                if add_compare:
                    headers += ['Atual', 'Anterior', 'Δ', 'Δ %']
                else:
                    headers += ['Valor']
                for col, h in enumerate(headers):
                    sheet.write(row, col, h, fmt_hdr)
                row += 1

                order = [
                    ('rev_gross','Receita Bruta'),
                    ('rev_deductions','Deduções de Receita'),
                    ('rev_net','Receita Líquida'),
                    ('cogs','COGS'),
                    ('gross_profit','Lucro Bruto'),
                    ('opex','Despesas Operacionais'),
                    ('op_result','Resultado Operacional'),
                    ('fin_income','Receitas Financeiras'),
                    ('fin_expense','Despesas Financeiras'),
                    ('fin_result','Resultado Financeiro'),
                    ('other_income','Outras Receitas'),
                    ('other_expense','Outras Despesas'),
                    ('ebt','EBT'),
                    ('tax_income','Impostos (IR/CSLL)'),
                    ('net_income','Lucro Líquido'),
                ]
                for key, label in order:
                    cur = vals.get(key, 0.0)
                    sheet.write(row, 0, label)
                    if add_compare:
                        pre = cmp.get(key, 0.0)
                        delta = dlt.get(key, 0.0)
                        pct = dpc.get(key, 0.0)
                        sheet.write_number(row, 1, cur, fmt_num_neg if cur < 0 else fmt_num)
                        sheet.write_number(row, 2, pre, fmt_num_neg if pre < 0 else fmt_num)
                        sheet.write_number(row, 3, delta, fmt_num_neg if delta < 0 else fmt_num)
                        sheet.write_number(row, 4, pct, fmt_pct)
                    else:
                        sheet.write_number(row, 1, cur, fmt_num_neg if cur < 0 else fmt_num)
                    row += 1

                # Aba Detalhe (contas do período atual)
                sheet2 = workbook.add_worksheet('Detalhe contas')
                r = 0
                sheet2.write(r, 0, "Seção", fmt_hdr)
                sheet2.write(r, 1, "Código", fmt_hdr)
                sheet2.write(r, 2, "Conta", fmt_hdr)
                sheet2.write(r, 3, "Valor", fmt_hdr)
                r += 1

                for sec, lines in bd.items():
                    for ln in lines:
                        sheet2.write(r, 0, sec)
                        sheet2.write(r, 1, ln.get('code') or '')
                        sheet2.write(r, 2, ln.get('name') or '')
                        amt = ln.get('amount', 0.0)
                        sheet2.write_number(r, 3, amt, fmt_num_neg if amt < 0 else fmt_num)
                        r += 1
else:
    # Stub inofensivo: mantém o registro do modelo para o Odoo não quebrar na carga.
    # A exportação em si é bloqueada no wizard com um UserError amigável.
    class ReportDREXlsx(models.AbstractModel):
        _name = 'report.ats_dre_report.report_dre_xlsx'
        _description = 'DRE XLSX Export (stub – instale OCA/report_xlsx para usar)'
        # sem métodos
        pass
