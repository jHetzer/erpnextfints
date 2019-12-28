# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _


def add_payment_reference(payment_entry, sales_invoice):
    """Add payment reference to payment entry for sales invoice.

    Create new bank account and if missing a bank entry.
    :param payment_entry: json formated payment_doc
    :param sales_invoice: json formated bank information
    :type payment_entry: str
    :type sales_invoice: str
    :return: Payment reference name
    """
    try:
        salesInvoiceDoc = frappe.get_doc(
            "Sales Invoice",
            sales_invoice
        )
        paymentEntryDoc = frappe.get_doc(
            "Payment Entry",
            payment_entry
        )

        reference_details = {
            "reference_doctype": "Sales Invoice",
            "reference_name": sales_invoice,
            "total_amount": salesInvoiceDoc.base_grand_total,
            "outstanding_amount": salesInvoiceDoc.outstanding_amount,
        }

        unallocated_amount = paymentEntryDoc.unallocated_amount

        # Adjust "Payment Entry Reference" "outstanding_amount" if
        # "Payment Entry" "paid_mount" is greater
        if unallocated_amount > 0:
            if unallocated_amount > reference_details["outstanding_amount"]:
                reference_details["allocated_amount"] = \
                    reference_details["outstanding_amount"]
            else:
                reference_details["allocated_amount"] = unallocated_amount

            new_row = paymentEntryDoc.append("references")
            new_row.docstatus = 1
            new_row.update(reference_details)

            paymentEntryDoc.flags.ignore_validate_update_after_submit = True
            paymentEntryDoc.setup_party_account_field()
            paymentEntryDoc.set_missing_values()
            paymentEntryDoc.set_amounts()
            paymentEntryDoc.save()

            if paymentEntryDoc.unallocated_amount == 0:
                paymentEntryDoc.submit()

            return new_row
        else:
            frappe.msgprint(_(
                "No unallocated amount found. Please refresh page"
            ))
    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        frappe.throw(_("Could not create payment reference: {0}").format(e))
        return False
