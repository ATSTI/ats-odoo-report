from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    rg = fields.Char(string='RG')
