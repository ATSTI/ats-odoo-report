from odoo import fields, models

class ReportComissaoWizard(models.TransientModel):
    _name = 'report.comissao.wizard'
    _description = 'Relatório de Comissão'

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
    comissao = fields.Float("Comissão(%)", default=5.0)

    def action_print_report(self):
        data = {
            'vendedor_ids': self.vendedor_id.ids,
            'data_inicial': self.data_inicial,
            'data_final': self.data_final,
            'comissao': self.comissao,
        }

        return self.env.ref(
            'report_fritisco.report_comissao_wizard'
        ).report_action(self, data=data)