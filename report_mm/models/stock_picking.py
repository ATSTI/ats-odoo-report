from odoo import models
from collections import OrderedDict


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_moves_grouped_by_section(self):
        self.ensure_one()

        # Pega a ordem de venda diretamente pelo picking
        sale_order = self.sale_id  # campo nativo do stock.picking

        if not sale_order:
            return {"Sem Seção": self.move_ids_without_package}

        # Monta o mapa: sale_line_id -> nome da seção
        section_map = {}
        current_section = "Sem Seção"
        for line in sale_order.order_line:
            if line.display_type == 'line_section':
                current_section = line.name
            elif not line.display_type:
                section_map[line.id] = current_section

        # Agrupa os moves preservando a ordem das seções
        grouped = OrderedDict()
        for move in self.move_ids_without_package.filtered(lambda m: not m.scrapped):
            section = section_map.get(move.sale_line_id.id, "Sem Seção")
            grouped.setdefault(section, self.env['stock.move'])
            grouped[section] |= move

        return grouped