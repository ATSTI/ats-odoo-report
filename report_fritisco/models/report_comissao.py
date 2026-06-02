from odoo import api, models,fields

class ReportComissao(models.AbstractModel):
    _name = 'report.report_fritisco.report_comissao_template'
    _description = 'Relatório de Comissão'

    @api.model
    def _get_report_values(self, docids, data=None):

        vendedor = self.env['res.users'].browse(
            data.get('vendedor_ids', [])
        )

        domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'paid'),
            ('invoice_date', '>=', data.get('data_inicial')),
            ('invoice_date', '<=', data.get('data_final')),
        ]

        if vendedor:
            domain.append(
                ('invoice_user_id', 'in', vendedor.ids)
            )

        invoices = self.env['account.move'].search(
            domain,
            order='invoice_user_id, invoice_date'
        )

        linhas = []
        total_vendido = 0
        total_comissao = 0
        comissao_percentual = data.get('comissao', 5.0)

        for invoice in invoices:

            comissao = invoice.amount_total * (comissao_percentual / 100)

            linhas.append({
                'vendedor': invoice.invoice_user_id.name,
                'cliente': invoice.partner_id.name,
                'nota': invoice.name,
                'emissao': invoice.invoice_date.strftime('%d/%m/%Y'),
                'valor_venda': invoice.amount_total,
                'percentual': comissao_percentual,
                'comissao': comissao,
            })

            total_vendido += invoice.amount_total
            total_comissao += comissao

        return {
        'docs': linhas,
        'vendedor': vendedor,
        'data_inicial': fields.Date.to_date(data.get('data_inicial')).strftime('%d/%m/%Y'),
        'data_final': fields.Date.to_date(data.get('data_final')).strftime('%d/%m/%Y'),
        'total_vendido': total_vendido,
        'total_comissao': total_comissao,
    }