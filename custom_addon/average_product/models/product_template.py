from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    average = fields.Float()

    @api.onchange('average')
    def _onchange_average(self):
        # print('h
        record = self._origin
        count = self.env['purchase.order.line'].search([('product_id.id', '=', record.id)])
        for rec in count:
            quantity = rec.product_uom_qty
            amount = rec.price_unit
            avg_amount = amount / quantity
            print(avg_amount)
            # total = 0
            # total += avg_amount

        # counts = len(count)
        # total = + avg_amount
        # print(sum(self.env['purchase.order.line'].search([('product_id.id', '=', record.id)])))
        # # print(len(purchase.order.line))
        # records = count.mapped('avg_amount')
        # print(records)
