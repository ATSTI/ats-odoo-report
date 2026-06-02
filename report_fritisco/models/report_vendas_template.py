from odoo import fields, models

class ReportVendasWizard(models.TransientModel):
    _name = 'report.vendas.wizard'
    _description = 'Relatório de Vendas'

    vendedor_id = fields.Many2one(
        'res.users',
        string='Vendedor'
    )

    data_inicial = fields.Date(
        string='Data Inicial',
        required=True
    )

    data_final = fields.Date(
        string='Data Final',
        required=True
    )

    def action_print_report(self):
        data = {
            'vendedor_ids': self.vendedor_id.ids,
            'data_inicial': self.data_inicial,
            'data_final': self.data_final,
        }

        return self.env.ref(
            'report_fritisco.report_vendas_wizard'
        ).report_action(self, data=data)