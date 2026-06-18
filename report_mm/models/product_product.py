from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_image_direction(self, direction, tipo=False, posicao=False):
        self.ensure_one()

        partes = []

        if tipo:
            partes.append(tipo.lower())

        if posicao:
            partes.append(posicao[:3].lower())

        if direction == 'Dir':
            partes.append('dir')
        elif direction == 'Esq':
            partes.append('esq')
        elif direction == 'dois lados':
            partes.append('doislados')

        arquivo = '_'.join(partes)

        return f"/report_mm/static/src/img/{arquivo}.png"