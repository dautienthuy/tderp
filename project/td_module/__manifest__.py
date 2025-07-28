# -*- coding: utf-8 -*-

{
    'name': 'Project Triduc Elevator',
    'version': '1.0',
    'sequence': 1,
    'category': 'Baaesoft Standard Modules',  
    'author': 'Baaesoft',
    'description': """
        This module will install all module dependencies of td_module.""",
    'depends': [
        'base',
        # 'web_chatter_position',
        # 'web_sheet_full_width',
        'contacts',
        'sale_management',
        'maintenance',
        #'documents',
        'hr',
        'stock',
        'delivery',
        'stock_sms'
        ],
    'summary': 'TD Project Module',
    'website': 'https://baaesoft.com',
    'data': [
        # SECURITY
        'security/maintenance_security.xml',
        #
        'security/ir.model.access.csv',
        # DATA
        # Wizards
        # VIEWS
        'views/maintenance/maintenance_views.xml',
        'views/maintenance/maintenance_equipment_views.xml',
        'views/maintenance/equipment_parts_list_views.xml',
        'views/maintenance/maintenance_checklist_views.xml',
        #
        'views/sale/sale_order_views.xml',
        # REPORT
        # MENU
        'menu/maintenance_menu.xml',
        # MENU - GROUP
        # POST OBJECT
        # Template
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'assets': {
    },
}
