# -*- coding: utf-8 -*-# noqa: D100
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _

def before_install():  # noqa: D103
    if frappe.utils.sys.version_info.major < 3:
        print(_("ERPNextFinTS requires Python version 3.4 or newer"))


def after_install():  # noqa: D103
    folder = 'Home/Attachments'
    foldername = 'FinTS'
    if not frappe.db.exists("File", {"file_name": foldername, "is_folder": True, "folder": folder}):
        folder = frappe.get_doc({
            "doctype": "File",
            "file_name": foldername,
            "is_folder": True,
            "folder": folder
        })
        folder.insert()