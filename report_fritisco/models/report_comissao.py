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
            ('payment_state', '=', 'paid'),  
        ]

        if vendedor_ids:
            domain.append(('invoice_user_id', 'in', vendedor_ids))

        invoices = self.env['account.move'].search(
            domain,
            order='invoice_user_id, invoice_date'
        )

        linhas = []
        total_vendido = 0.0
        total_comissao = 0.0
        comissao_percentual = float(data.get('comissao', 5.0) or 0.0)
        data_inicial = fields.Date.to_date(data.get('data_inicial')) if data.get('data_inicial') else None
        data_final = fields.Date.to_date(data.get('data_final')) if data.get('data_final') else None

        for invoice in invoices:
            payments = invoice._get_reconciled_payments().sorted(
                key=lambda p: p.date or fields.Date.today()
            )

            parcela_num = 0

            for payment in payments:

                payment_date = payment.date

                if data_inicial and payment_date < data_inicial:
                    continue

                if data_final and payment_date > data_final:
                    continue

                parcela_num += 1

                valor_pago = abs(payment.amount)

                comissao = valor_pago * (comissao_percentual / 100.0)

                linhas.append({
                    'vendedor': invoice.invoice_user_id.name,
                    'cliente': invoice.partner_id.name,
                    'nota': invoice.name,
                    'emissao': invoice.invoice_date.strftime('%d/%m/%Y') if invoice.invoice_date else '',

                    'parcela': parcela_num,
                    'data_pagamento': payment_date,

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