from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    numero_orcamento = fields.Char(
        string='Nº do Orçamento',
        copy=False,
        readonly=True,
    )

    date_order_month = fields.Selection(
            [
                ('01', 'Janeiro'),
                ('02', 'Fevereiro'),
                ('03', 'Março'),
                ('04', 'Abril'),
                ('05', 'Maio'),
                ('06', 'Junho'),
                ('07', 'Julho'),
                ('08', 'Agosto'),
                ('09', 'Setembro'),
                ('10', 'Outubro'),
                ('11', 'Novembro'),
                ('12', 'Dezembro'),
            ],
            string='Mês do Pedido',
            compute='_compute_date_order_month',
            store=True,
        )

    # purchase_order_id = fields.Many2one('purchase.order', string='Pedido de Compra de Origem')

    numero_pedido_compra = fields.Char(
        string='Nº do Pedido de Compra',

        store=True,
    )

    moeda_cotacao = fields.Selection([
        ('USD', 'Dólar'),
        ('BRL', 'Real'),
    ], string='Moeda da cotação', default='USD')

    def action_confirm(self):
        res = super().action_confirm()

        for order in self:
            if not order.numero_orcamento:
                order.numero_orcamento = order.name

        return res

    @api.depends('date_order')
    def _compute_date_order_month(self):
        for order in self:
            if order.date_order:
                local_dt = fields.Datetime.context_timestamp(order, order.date_order)
                order.date_order_month = '%02d' % local_dt.month
            else:
                order.date_order_month = False