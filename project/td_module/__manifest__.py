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
        'web_chatter_position',
        'web_sheet_full_width',
        'contacts',        
        'sale_management',
        'maintenance',
        'documents',
        'hr',
        ],
    'summary': 'TD Project Module',
    'website': 'https://baaesoft.com',
    'data': [
        # SECURITY
        # DATA
        # Wizards
        # VIEWS
        'views/maintenance/maintenance_equipment_views.xml',
        # REPORT
        # MENU
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
