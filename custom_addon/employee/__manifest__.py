{
    'name':"Employee Transfer ",
    'author':'odoo',
    'version':'17.0.4.0',
    'category':'Employee',
    'summary':'Transfer',
    'license': 'GPL-2',
    'sequence':-10,
    'installation': True,
    'application': True,
    'depends':['base',
               'hr'],
    'data':[
        'security/res_groups.xml',
        'security/ir_rules.xml',
        'security/ir.model.access.csv',
        'views/employee_transfer_views.xml',
        ],
}