from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_moves_grouped_by_section(self):
        self.ensure_one()

        grouped = {}
        current_section = "Sem Seção"

        sale_lines = self.move_ids_without_package.mapped('sale_line_id.order_id.order_line')
        sale_order = sale_lines[:1].order_id

        if not sale_order:
            return {"Sem Seção": self.move_ids_without_package}

        section_map = {}

        current_section = "Sem Seção"
        for line in sale_order.order_line:
            if line.display_type == 'line_section':
                current_section = line.name
            elif not line.display_type:
                section_map[line.id] = current_section

        for move in self.move_ids_without_package.filtered(lambda m: not m.scrapped):
            section = section_map.get(
                move.sale_line_id.id,
                "Sem Seção"
            )
            grouped.setdefault(section, self.env['stock.move'])
            grouped[section] |= move

        return grouped