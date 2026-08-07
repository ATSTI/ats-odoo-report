from odoo import api, models, fields


class ReportComissao(models.AbstractModel):
    _name = 'report.report_fritisco.report_comissao_template'
    _description = 'Relatório de Comissão'

    @api.model
    def _get_report_values(self, docids, data=None):

        data = data or {}

        vendedor_ids = data.get('vendedor_ids', [])
        vendedor = self.env['res.users'].browse(vendedor_ids)

        domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
             ('payment_state', 'in', ['paid', 'partial']),
        ]

        if vendedor_ids:
            domain.append(('invoice_user_id', 'in', vendedor_ids))

        invoices = self.env['account.move'].search(
            domain,
            order='invoice_user_id, partner_id, invoice_date'
        )

        linhas = []
        total_vendido = 0.0
        total_comissao = 0.0

        comissao_percentual = float(data.get('comissao', 5.0) or 0.0)

        data_inicial = fields.Date.to_date(data.get('data_inicial')) if data.get('data_inicial') else None
        data_final = fields.Date.to_date(data.get('data_final')) if data.get('data_final') else None

        for invoice in invoices:

            receivable_lines = invoice.line_ids.filtered(   
                lambda l: l.account_id.account_type == 'asset_receivable'
            )

            partials = self.env['account.partial.reconcile'].search([
                '|',
                ('debit_move_id', 'in', receivable_lines.ids),
                ('credit_move_id', 'in', receivable_lines.ids),
            ], order='id')

            parcela_num = 0

            for p in partials:

                debit = p.debit_move_id
                credit = p.credit_move_id
                payment_move = debit.move_id if debit.move_id.move_type == 'entry' else credit.move_id
                payment_date = payment_move.date if payment_move else False
                if not payment_date:
                    continue

                if data_inicial and payment_date < data_inicial:
                    continue

                if data_final and payment_date > data_final:
                    continue

                parcela_num += 1

                valor_pago = abs(p.amount)
                comissao = valor_pago * (comissao_percentual / 100.0)

                sale_orders = invoice.invoice_line_ids.mapped('sale_line_ids.order_id')
                referencia = ', '.join(sale_orders.mapped('name')) if sale_orders else (invoice.invoice_origin or invoice.name)

                linhas.append({
                    'vendedor': invoice.invoice_user_id.name,
                    'cliente': invoice.partner_id.name,
                    'referencia': referencia,
                    'emissao': invoice.invoice_date.strftime('%d/%m/%Y') if invoice.invoice_date else '',
                    'forma_pagamento': invoice.payment_mode_id.name if invoice.payment_mode_id else '',
                    'parcela': parcela_num,

                    'data_pagamento': payment_date.strftime('%d/%m/%Y'),

                    'valor_pago': valor_pago,
                    'percentual': comissao_percentual,
                    'comissao': comissao,
                })

                total_vendido += valor_pago
                total_comissao += comissao

        return {
            'docs': linhas,
            'vendedor': vendedor,
            'data_inicial': data_inicial.strftime('%d/%m/%Y') if data_inicial else '',
            'data_final': data_final.strftime('%d/%m/%Y') if data_final else '',
            'total_vendido': total_vendido,
            'total_comissao': total_comissao,
        }