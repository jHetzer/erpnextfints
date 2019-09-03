from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
        {
            "label": _("Integrations"),
            "icon": "octicon octicon-git-compare",
            "items": [
                   {
                       "type": "doctype",
                       "name": "FinTS Import",
                       "label": _("FinTS Import"),
                       "description": _("FinTS Import")
                   },
                   {
                       "type": "doctype",
                       "name": "FinTS Login",
                       "label": _("FinTS Login"),
                       "description": _("FinTS Login")
                   },
                   {
                       "type": "doctype",
                       "name": "FinTS Schedule",
                       "label": _("FinTS Schedule"),
                       "description": _("FinTS Schedule")
                   }
            ]
        }
]
