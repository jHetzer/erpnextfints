# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import throw, _
from frappe.core.doctype.file.file import create_new_folder

def before_install():
    if frappe.utils.sys.version_info.major < 3:
        print(_("ERPNextFinTS requires Python version 3.4 or newer"))

def after_install():
    folder = 'Home/Attachments'
    foldername = 'FinTS'
    if not frappe.db.exists('File', {'name': "/".join([folder, foldername])}):
        create_new_folder(foldername, folder)
