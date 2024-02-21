{
    "name": "Farm",
    "summary": """Farm""",
    "description": """Farm""",
    "author": "Cris-aian Vergara",
    "website": "https://www.crisaianvergara.com",
    "category": "Farm",
    "version": "17.0.1.0.0",
    "depends": ["base"],
    "data": [
      "security/security.xml",
      "security/ir.model.access.csv",

      "views/farm_menus.xml",

      # Farm
      "views/farm_farm_views.xml",
      # Configuration
      "views/farm_crop_views.xml",
      "views/farm_field_views.xml",
      "views/farm_location_views.xml",
      "views/farm_task_views.xml",
      "views/farm_type_views.xml",
      "views/farm_uom_views.xml",
    ],
    "demo": [],
    "assets": {},
    "sequence": -96,
    "application": True,
    "installable": True,
    "license": "LGPL-3"
}