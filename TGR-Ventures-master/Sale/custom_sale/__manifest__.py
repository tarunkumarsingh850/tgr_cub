# -*- coding: utf-8 -*-
{
    'name': "Sale Order Management",
    'summary': """Sale Order Management.""",
    'description': """Sale Order Management
    """,
    'author': "",
    'website': "",
    'category': 'Tools',
    'version': '15.0.0.1',
    'depends': ['base', 'sale', 'stock_picking_batch'],
    'data': [
    	'security/ir.model.access.csv',
        'report/report.xml',
        'report/priority_group_template.xml',
        'views/priority_group_master_views.xml',
        'views/inherit_sale_order_view.xml',
        'views/inherit_stock_picking_batch_view.xml',
        'wizard/wiz_sale_priority_group_views.xml'
    ],
    'qweb': [
    ],
    'images': [],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
