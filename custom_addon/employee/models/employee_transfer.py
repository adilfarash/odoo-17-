from odoo import fields, models


class EmployeeTransfer(models.Model):
    _name = 'employee.transfer'
    _description = 'Employee Transfer'
    _rec_name = 'employee_id'
    _inherit = 'mail.thread'

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True)
    company_id = fields.Many2one(related='employee_id.company_id', string='Company Name')
    company_country_id = fields.Many2one(related='employee_id.company_country_id')
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('to_approve', 'To Approve'),
                                        ('transfer', 'Approved')], default='draft')
    transfer_company_id = fields.Many2one(comodel_name='res.company', required=True)

    def action_approve(self):
        """Approve button to approve the transfer and change the state"""
        self.write({
            'state': 'transfer'
        })
        # self.env['hr.employee'].write([
        #     {
        #         'company_id': self.company_id,
        #
        #     }
        # ])
        self.employee_id.write({
            'company_id': self.transfer_company_id.id
        })

    def action_to_approve(self):
        """to approve button to get  request from a user for a transfer approve"""
        self.write({
            'state': 'to_approve',
        })
