{
    'name': "PDF Demo",
    # 'version': '17.1.0.0',
    'category': 'sales',
    'summary': 'demo app',
    'summery': 'PDF',
    'depends': ['web',
                'sale_management',
                'stock',
                ],
    'data': [
        'data/paper_format.xml',
        'report/report_layout.xml',
    ],
    'external_dependencies': {
        'python': ['matplotlib'],
    },
    'license': 'LGPL-3',
    'installation': True,
    'auto_install': False,
    'application': False,

}
