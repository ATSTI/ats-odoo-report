# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import timedelta
from calendar import monthrange
from dateutil.relativedelta import relativedelta

from odoo import fields, models
from odoo.exceptions import UserError


class DREReportWizard(models.TransientModel):
    _name = 'dre.report.wizard'
    _description = 'Wizard DRE (ATS)'

    company_id = fields.Many2one(
        'res.company', string='Empresa', required=True,
        default=lambda self: self.env.company
    )
    date_from = fields.Date(
        string='De', required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1)
    )
    date_to = fields.Date(
        string='Até', required=True,
        default=fields.Date.context_today
    )
    target_move = fields.Selection(
        [('posted', 'Somente Postados'), ('all', 'Todos')],
        default='posted', required=True
    )
    add_compare = fields.Boolean(
        string='Comparar com período anterior',
        default=True
    )
    compare_mode = fields.Selection(
        [
            ('prev_period', 'Período anterior (mesma duração)'),
            ('prev_month', 'Mês anterior'),
            ('yoy', 'Mesmo período do ano anterior (YoY)'),
        ],
        string='Modo de comparação',
        default='prev_period'
    )

    # -------------------- helpers --------------------

    def _domain_move_lines(self, dfrom, dto):
        domain = [
            ('company_id', '=', self.company_id.id),
            ('date', '>=', dfrom),
            ('date', '<=', dto),
        ]
        if self.target_move == 'posted':
            domain.append(('parent_state', '=', 'posted'))
        return domain

    def _map_account_to_section(self, account):
        """Mapeia a conta para a seção do DRE."""
        # Se você tiver um campo custom 'dre_section' no account, ele tem prioridade:
        if getattr(account, 'dre_section', False):
            return account.dre_section

        t = account.account_type
        if t in ('income', 'other_income'):
            return 'rev_gross'
        if t in ('direct_cost',):
            return 'cogs'
        if t in ('expense',):
            return 'opex'
        # Ajuste aqui se quiser mapear receitas/despesas financeiras, outras, impostos etc.
        return False  # ignora no DRE

    def _is_full_single_month(self):
        """True se o período cobre exatamente um mês calendário inteiro."""
        df, dt = self.date_from, self.date_to
        return (
            df and dt and
            df.year == dt.year and df.month == dt.month and
            df.day == 1 and dt.day == monthrange(df.year, df.month)[1]
        )

    def _compute_compare_range(self):
        """Calcula o intervalo comparativo conforme compare_mode."""
        if self.compare_mode == 'prev_period':
            days = (self.date_to - self.date_from).days + 1
            prev_to = self.date_from - timedelta(days=1)
            prev_from = prev_to - timedelta(days=days - 1)
            return prev_from, prev_to, 'Período anterior'

        if self.compare_mode == 'prev_month':
            if self._is_full_single_month():
                ref = self.date_from - relativedelta(months=1)
                prev_from = ref.replace(day=1)
                prev_to = ref.replace(day=monthrange(ref.year, ref.month)[1])
            else:
                prev_from = self.date_from - relativedelta(months=1)
                prev_to = self.date_to - relativedelta(months=1)
            return prev_from, prev_to, 'Mês anterior'

        if self.compare_mode == 'yoy':
            prev_from = self.date_from - relativedelta(years=1)
            prev_to = self.date_to - relativedelta(years=1)
            return prev_from, prev_to, 'Ano anterior (YoY)'

        # fallback
        days = (self.date_to - self.date_from).days + 1
        prev_to = self.date_from - timedelta(days=1)
        prev_from = prev_to - timedelta(days=days - 1)
        return prev_from, prev_to, 'Período anterior'

    def _aggregate(self, dfrom, dto, with_breakdown=False):
        """Soma valores por seção e (opcionalmente) por conta."""
        aml = self.env['account.move.line'].search(self._domain_move_lines(dfrom, dto))
        totals = defaultdict(float)
        breakdown = defaultdict(dict) if with_breakdown else None

        for line in aml:
            sec = self._map_account_to_section(line.account_id)
            if not sec:
                continue
            # Convenção de sinal: receitas positivas, despesas negativas
            amount = -(line.balance or 0.0)
            if not amount:
                continue

            totals[sec] += amount

            if with_breakdown:
                acc = line.account_id
                rec = breakdown[sec].get(acc.id)
                if not rec:
                    rec = breakdown[sec][acc.id] = {
                        "id": acc.id,
                        "code": acc.code or "",
                        "name": acc.name or "",
                        "amount": 0.0,
                    }
                rec["amount"] += amount

        data = {
            'rev_gross': totals.get('rev_gross', 0.0),
            'rev_deductions': totals.get('rev_deductions', 0.0),
            'cogs': totals.get('cogs', 0.0),
            'opex': totals.get('opex', 0.0),
            'fin_income': totals.get('fin_income', 0.0),
            'fin_expense': totals.get('fin_expense', 0.0),
            'other_income': totals.get('other_income', 0.0),
            'other_expense': totals.get('other_expense', 0.0),
            'tax_income': totals.get('tax_income', 0.0),
        }
        data['rev_net'] = data['rev_gross'] + data['rev_deductions']
        data['gross_profit'] = data['rev_net'] + data['cogs']
        data['op_result'] = data['gross_profit'] + data['opex']
        data['fin_result'] = data['fin_income'] + data['fin_expense']
        data['ebt'] = data['op_result'] + data['fin_result'] + data['other_income'] + data['other_expense']
        data['net_income'] = data['ebt'] + data['tax_income']

        if with_breakdown:
            data['breakdown'] = {
                sec: sorted(
                    [v for v in acc_map.values() if v.get("amount")],
                    key=lambda x: (x.get("code") or "", x.get("name") or "")
                )
                for sec, acc_map in breakdown.items()
            }
        return data

    # -------------------- API --------------------

    def get_data(self):
        """Monta o payload final para o relatório."""
        # atual (com detalhe por contas)
        current = self._aggregate(self.date_from, self.date_to, with_breakdown=True)

        # comparativo
        comp = {}
        comp_breakdown = {}
        delta = {}
        delta_pct = {}
        compare_label = 'Anterior'
        prev_from = prev_to = False

        if self.add_compare:
            prev_from, prev_to, compare_label = self._compute_compare_range()
            comp = self._aggregate(prev_from, prev_to, with_breakdown=False)
            comp_det = self._aggregate(prev_from, prev_to, with_breakdown=True)
            comp_breakdown = comp_det.get('breakdown', {})

            keys = [
                'rev_gross','rev_deductions','rev_net','cogs','gross_profit',
                'opex','op_result','fin_income','fin_expense','fin_result',
                'other_income','other_expense','ebt','tax_income','net_income'
            ]
            for k in keys:
                cur = current.get(k, 0.0)
                pre = comp.get(k, 0.0)
                d = cur - pre
                delta[k] = d
                delta_pct[k] = (d / abs(pre)) if pre else 0.0

        # juntar detalhe atual + anterior por conta (mesma linha) + Δ e Δ%
        breakdown_joined = {}
        cur_bd = current.get('breakdown', {})
        for sec, lines in cur_bd.items():
            prev_index = {x['id']: x for x in comp_breakdown.get(sec, [])}
            out = []
            for ln in lines:
                cur_amt = ln.get('amount', 0.0)
                prev_amt = prev_index.get(ln['id'], {}).get('amount', 0.0)
                d = cur_amt - prev_amt
                pct = (d / abs(prev_amt)) if prev_amt else 0.0
                item = dict(ln)
                item['prev'] = prev_amt
                item['delta'] = d
                item['delta_pct'] = pct
                out.append(item)
            breakdown_joined[sec] = out

        # pacote final
        current['comp'] = comp
        current['breakdown_prev'] = comp_breakdown
        current['breakdown_joined'] = breakdown_joined
        current['delta'] = delta
        current['delta_pct'] = delta_pct
        current['add_compare'] = bool(self.add_compare)
        current['compare_label'] = compare_label
        current['prev_date_from'] = prev_from
        current['prev_date_to'] = prev_to
        return current

    def action_view_html(self):
        return self.env.ref('ats_dre_report.action_report_dre_html').report_action(self)

    def action_view_pdf(self):
        return self.env.ref('ats_dre_report.action_report_dre_pdf').report_action(self)

    def action_export_xlsx(self):
        # Verifica se o engine XLSX (OCA/report_xlsx) está instalado
        has_xlsx = self.env['ir.module.module'].sudo().search([
            ('name', '=', 'report_xlsx'),
            ('state', '=', 'installed')
        ], limit=1)
        if not has_xlsx:
            raise UserError(
                "Para exportar XLSX é necessário instalar o módulo OCA 'report_xlsx'.\n"
                "👉 Passos: coloque o repositório em seu addons_path e instale o módulo 'report_xlsx'."
            )
        return self.env.ref('ats_dre_report.action_report_dre_xlsx').report_action(self)
