{
    'name': 'kb_mrp_production',
    'version': '13.0.1.0.0',
    'category': 'manufacturing',
    'summary': 'kb_mrp_production',
    'description': """ Ini adalah Module kb_mrp_production """,
    'website': '',
    'author': 'KB',
    'depends': ['web','base','mrp','stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/kb_mrp_production_view.xml',
        'views/kb_mrp_production_action.xml',
        'views/kb_mrp_production_menuitem.xml',
        'views/kb_mrp_production_sequence.xml',
        'reports/kb_mrp_production_report.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OEEL-1',
}