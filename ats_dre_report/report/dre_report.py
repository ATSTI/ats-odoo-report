# -*- coding: utf-8 -*-
from odoo import api, models

class ReportDRE(models.AbstractModel):
    _name = 'report.ats_dre_report.report_dre_template'
    _description = 'Report DRE Renderer'

    def _format_br(self, n):
        try:
            s = f"{float(n):,.2f}"
        except Exception:
            s = "0.00"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")

    def _format_pct(self, n):
        try:
            s = f"{float(n)*100:,.2f}%"
        except Exception:
            s = "0.00%"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['dre.report.wizard'].browse(docids)
        payload = {}
        if docs:
            payload = docs[0].get_data()

        act_posted = self.env.ref('ats_dre_report.action_open_move_lines_posted').id
        act_all = self.env.ref('ats_dre_report.action_open_move_lines_all').id

        return {
            'doc_ids': docids,
            'doc_model': 'dre.report.wizard',
            'docs': docs,
            'data': payload,
            'breakdown': payload.get('breakdown', {}),
            'breakdown_prev': payload.get('breakdown_prev', {}),
            'breakdown_joined': payload.get('breakdown_joined', {}),  # << novo
            'format_br': self._format_br,
            'format_pct': self._format_pct,
            'add_compare': payload.get('add_compare', False),
            'comp': payload.get('comp', {}),
            'delta': payload.get('delta', {}),
            'delta_pct': payload.get('delta_pct', {}),
            'compare_label': payload.get('compare_label', 'Anterior'),
            'prev_date_from': payload.get('prev_date_from', False),
            'prev_date_to': payload.get('prev_date_to', False),
            'act_posted_id': act_posted,
            'act_all_id': act_all,
        }
