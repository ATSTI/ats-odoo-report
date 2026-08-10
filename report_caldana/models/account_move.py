from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    data_de_entrega = fields.Date(string='Data de Entrega', help='Data de entrega', store=True)
