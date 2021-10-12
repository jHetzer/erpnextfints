# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe.model.document import Document
from dateutil.relativedelta import relativedelta
from frappe.utils import now_datetime
from frappe.utils.scheduler import is_scheduler_inactive
from frappe import _
from erpnextfints.utils.client import import_fints_transactions
from erpnextfints.utils.fints_controller import FinTSController
# import erpnextfints.erpnextfints.doctype.fints_import.fints_import as fin_imp
# from erpnextfints.utils.fints_wrapper import FinTSConnection


class FinTSSchedule(Document):
    def validate(self):  # pylint: disable=no-self-use
        if is_scheduler_inactive():
            frappe.throw(
                _("Scheduler is inactive. Cannot import data."),
                title=_("Scheduler Inactive")
            )


@frappe.whitelist()
def scheduled_import_fints_payments(manual=None):
    """Create payment entries by FinTS Schedule.

    :param manual: Call manualy
    :type manual: bool
    :return: None
    """
    schedule_settings = frappe.get_single('FinTS Schedule')

    # Query child table
    for child_item in schedule_settings.schedule_items:
        # Get the last run / last imported transaction date
        try:
            if child_item.active and (child_item.import_frequency or manual):
                lastruns = frappe.get_list(
                    'FinTS Import',
                    filters={
                        'fints_login': child_item.fints_login,
                        'docstatus': 1,
                        'end_date': ('>', '1/1/1900')
                    },
                    fields=['name', 'end_date', 'modified'],
                    order_by='end_date desc, modified desc'
                )[:1] or [None]
                # Create new 'FinTS Import' doc
                fints_import = frappe.get_doc({
                    'doctype': 'FinTS Import',
                    'fints_login': child_item.fints_login
                })
                if lastruns[0] is not None:
                    if child_item.import_frequency == 'Daily':
                        checkdate = (
                            now_datetime().date() - relativedelta(days=1)
                        )
                    elif child_item.import_frequency == 'Weekly':
                        checkdate = (
                            now_datetime().date() - relativedelta(weeks=1)
                        )
                    elif child_item.import_frequency == 'Monthly':
                        checkdate = (
                            now_datetime().date() - relativedelta(months=1)
                        )
                    else:
                        raise ValueError('Unknown frequency')

                    new_from_date = (
                        lastruns[0].end_date + relativedelta(days=1)
                    )
                    if (
                        new_from_date < now_datetime().date() and (
                            lastruns[0].end_date < checkdate or manual
                        )
                    ):
                        fints_import.from_date = new_from_date
                        # overlap = child_item.overlap
                        # if overlap < 0:
                        #    overlap = 0
                    else:
                        frappe.db.rollback()
                        print("skip")
                        continue

                    # fints_import.from_date = lastruns[0].end_date - relativedelta(days=overlap) # noqa: E501
                # else: load all available transactions of the past
                # always import transactions from yesterday
                fints_import.to_date = \
                    now_datetime().date() - relativedelta(days=1)

                fints_import.save()
                if manual:
                    import_fints_transactions(
                        fints_import.name,
                        child_item.fints_login,
                        schedule_settings.name
                    )
                else:
                    FinTSController(child_item.fints_login) \
                        .import_fints_transactions(fints_import.name)
                # fin_imp.import_transactions(fints_import.name, child_item.fints_login) # noqa: E501

                print(frappe.as_json(child_item))
        except Exception:
            frappe.log_error(frappe.get_traceback())
