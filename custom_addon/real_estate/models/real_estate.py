from odoo import models, fields
from dateutil.relativedelta import relativedelta


class RealEstate(models.Model):
    _name = 'real.estate'
    _description = 'Real Estate'

    name = fields.Char(required=True, default="Enter Your Name")
    description = fields.Text(string="description")
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=fields.Date.today() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default='2')
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Type',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')], default='north')

    # def create(self, vals_list):
    #     print(self)
    #     print(vals_list)
    #     vals_list['name'] = 'tyujnewbghd'
    #     return super(RealEstate, self).create(vals_list)
