from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_lines_grouped_by_ambiente(self):
        """Agrupa as linhas do pedido de venda por ambiente (line_section).

        Cada section marca o início de um novo ambiente. As linhas de
        produto seguintes (até o próximo section) são agrupadas em um
        único item: a quantidade é somada, os nomes dos produtos são
        concatenados e o valor total do grupo é somado.
        """
        self.ensure_one()
        groups = []
        current_lines = []
        current_section_name = "Sem Seção"  # armazena nome sessao padrao caso n tenha

        def _flush():
            if current_lines:
                groups.append({
                    'section_name': current_section_name,
                    'qty': sum(l.product_uom_qty for l in current_lines),
                    'names': ' /// '.join(
                        l.product_id.display_name for l in current_lines if l.product_id
                    ),
                    'price': sum(l.price_subtotal for l in current_lines),
                })

        for line in self.sale_id.order_line:
            if line.display_type == 'line_section':
                _flush()
                current_lines = []
                current_section_name = line.name
            elif line.display_type == 'line_note':
                continue
            else:
                current_lines.append(line)

        _flush()
        return groups