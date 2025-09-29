from odoo import models, tools, _, fields
from odoo.exceptions import UserError
import base64

class MailTemplate(models.Model):
    _inherit = 'mail.template'

    report_template = fields.Many2many(
        comodel_name='ir.actions.report',
        string='Optional reports to print and attach'
    )

    def generate_email(self, res_ids, fields):
        """Versão adaptada para suportar vários relatórios (Many2many) 
        e anexar automaticamente relatórios específicos."""
        self.ensure_one()
        multi_mode = True
        if isinstance(res_ids, int):
            res_ids = [res_ids]
            multi_mode = False

        results = dict()
        for lang, (template, template_res_ids) in self._classify_per_lang(res_ids).items():

            for field in fields:
                generated_field_values = template._render_field(
                    field, template_res_ids,
                    post_process=(field == 'body_html')
                )
                for res_id, field_value in generated_field_values.items():
                    results.setdefault(res_id, dict())[field] = field_value

            if any(field in fields for field in ['email_to', 'partner_to', 'email_cc']):
                results = template.generate_recipients(results, template_res_ids)

            for res_id in template_res_ids:
                values = results[res_id]
                if values.get('body_html'):
                    values['body'] = tools.html_sanitize(values['body_html'])
                scheduled_date = values.pop('scheduled_date', None)
                if 'scheduled_date' in fields and scheduled_date:
                    parsed_datetime = self.env['mail.mail']._parse_scheduled_datetime(scheduled_date)
                    values['scheduled_date'] = parsed_datetime.replace(tzinfo=None) if parsed_datetime else False

                values.update(
                    mail_server_id=template.mail_server_id.id or False,
                    auto_delete=template.auto_delete,
                    model=template.model,
                    res_id=res_id or False,
                    attachment_ids=[attach.id for attach in template.attachment_ids],
                )

            
            default_reports = self.env['ir.actions.report'].search([
                ('report_name', 'in', [
                    'report_mm.report_orcamento_mmportas'
                    'report_mm.report_contrato_mmportas',
                    'report_mm.report_ambos_mmportas',
                    'report_mm.report_contrato_stand_mmportas',
                    'report_mm.report_contrato_orcamento_stand_mmportas',
                ])
            ])

            for res_id in template_res_ids:
                attachments = results[res_id].setdefault('attachments', [])
                report_display_names = results[res_id].setdefault('report_names', [])

                for report in default_reports:
                    report_name = report.name
                    report_display_names.append(report_name)

                    if report.report_type in ['qweb-html', 'qweb-pdf']:
                        result, report_format = self.env['ir.actions.report']._render_qweb_pdf(report, [res_id])
                    else:
                        res = self.env['ir.actions.report']._render(report, [res_id])
                        if not res:
                            raise UserError(_('Unsupported report type %s found.', report.report_type))
                        result, report_format = res

                    result = base64.b64encode(result)

                    ext = "." + report_format
                    if not report_name.endswith(ext):
                        report_name += ext

                    attachments.append((report_name, result))

        return multi_mode and results or results[res_ids[0]]
