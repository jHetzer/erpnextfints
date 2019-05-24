# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
from dateutil.relativedelta import relativedelta
from datetime import datetime
import erpnextfints.erpnextfints.doctype.fints_import.fints_import as fin_imp
# from erpnextfints.utils.fints_wrapper import FinTSConnection

class FinTSSchedule(Document):
    pass

@frappe.whitelist()
def import_fints_payments(manual=None):

    schedule_settings = frappe.get_single('FinTS Schedule')

    # Query child table
    for child_item in schedule_settings.schedule_items:
        # Get the last run / last imported transaction date
        try:
            if child_item.active and (child_item.import_frequency or manual):
                lastruns = frappe.get_list(
                    'FinTS Import',
                    filters={
                        'fints_login':child_item.fints_login,
                        'docstatus': 1,
                        "end_date": (">","1/1/1900")
                    },
                    fields=['name', 'end_date'],
                    order_by='end_date desc'
                )[:1] or [None]
                # Create new 'FinTS Import' doc
                fints_import = frappe.get_doc({
                    'doctype': 'FinTS Import',
                    'fints_login':child_item.fints_login
                })
                if lastruns[0] is not None:
                    if child_item.import_frequency == 'Daily':
                        checkdate = datetime.today().date() - relativedelta(days=1)
                    elif child_item.import_frequency == 'Weekly':
                        checkdate = datetime.today().date() - relativedelta(weeks=1)
                    elif child_item.import_frequency == 'Monthly':
                        checkdate = datetime.today().date() - relativedelta(months=1)
                    else:
                        raise Exception("Unknown frequency")
                    if lastruns[0].end_date < checkdate or manual:
                        overlap = child_item.overlap
                        if overlap < 0:
                            overlap = 0
                    else:
                        frappe.db.rollback()
                        print("skip")
                        continue
                    fints_import.from_date = lastruns[0].end_date - relativedelta(days=overlap)
                # else: load all available transactions

                fints_import.save()
                print(frappe.as_json(fints_import))
                fin_imp.import_transactions(fints_import.name, child_item.fints_login)

                print(frappe.as_json(child_item))
        except Exception as e:
            frappe.log_error(frappe.get_traceback())
