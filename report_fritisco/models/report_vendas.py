from odoo import api, models,fields

class ReportVendas(models.AbstractModel):
    _name = 'report.report_fritisco.report_vendas_template'
    _description = 'Relatório de Vendas'

    @api.model
    def _get_report_values(self, docids, data=None):

        vendedor = self.env['res.users'].browse(
            data.get('vendedor_ids', [])
        )

        domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', data.get('data_inicial')),
            ('invoice_date', '<=', data.get('data_final')),
        ]

        if vendedor:
            domain.append(
                ('invoice_user_id', 'in', vendedor.ids)
            )

        invoices = self.env['account.move'].search(
            domain,
            order='invoice_user_id, partner_id, invoice_date'
        )

        linhas = []

        for invoice in invoices:

            parcelas = invoice.line_ids.filtered(
                lambda l: l.display_type == 'payment_term'
            )

            total_parcelas = len(parcelas)

            for indice, parcela in enumerate(parcelas, start=1):
                if invoice.payment_state == 'paid':
                    situacao = 'Pago'
                else:
                    situacao = 'À Vencer'

                linhas.append({
                    'vendedor': invoice.invoice_user_id.name,
                    'cliente': invoice.partner_id.name,
                    'pedido': invoice.document_number,
                    'emissao': invoice.invoice_date.strftime('%d/%m/%Y') if invoice.invoice_date else '',
                    'parcela': f'{indice}/{total_parcelas}',
                    'vencimento': parcela.date_maturity.strftime('%d/%m/%Y') if parcela.date_maturity else '',
                    'valor_parcela': abs(parcela.balance),
                    'situacao': situacao,
                })


        return {
            'docs': linhas,
            'vendedor': vendedor,
            'data_inicial': fields.Date.to_date(data.get('data_inicial')).strftime('%d/%m/%Y'),
            'data_final': fields.Date.to_date(data.get('data_final')).strftime('%d/%m/%Y'),
        }