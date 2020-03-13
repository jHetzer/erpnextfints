# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
import os
from frappe import _


class AssignmentController:
    def __init__(self):
        self.cur_dir = os.path.dirname(__file__)

    @staticmethod
    def __read_sqlFile(name):
        cur_dir = os.path.dirname(__file__)
        file_path = os.path.join(cur_dir, './sql/' + name)
        with open(file_path) as file:
            sqlQuery = file.read()

        return sqlQuery

    def payment_to_saleInvoice(self):
        """Get one by one assignable payments.

        :return: List of assignable payments
        """
        sqlFile = "payment_to_saleInvoice.sql"
        return frappe.db.sql(self.__read_sqlFile(sqlFile), as_dict=True)

    def payments_to_saleInvoice(self):
        """Get many by one assignable payments.

        :return: List of assignable payments
        """
        sqlFile = "payments_to_saleInvoice.sql"
        return frappe.db.sql(self.__read_sqlFile(sqlFile), as_dict=True)

    def auto_assign_payments(self):
        """Query assignable payments and create payment references.

        Try to assign payments in 3 steps:
        1. payment to sale assingment
        2. multiple payments to sale assingment
        3. payment to sale assingment

        :return: List of assigned payments
        """
        assigners = [
            self.payment_to_saleInvoice,
            self.payments_to_saleInvoice,
            self.payment_to_saleInvoice
        ]
        matched_payments = []
        for methode in assigners:
            assignable_Payments = methode()

            for item in assignable_Payments:
                try:
                    self.add_payment_reference(
                        payment_entry=item["PaymentName"],
                        sales_invoice=item["SaleName"]
                    )
                    matched_payments.append(item)
                except Exception:
                    frappe.log_error(frappe.get_traceback())
                    # Revert references
                    payment_doc = frappe.get_doc(
                        "Payment Entry",
                        item["PaymentName"]
                    )
                    if payment_doc.references:
                        for i in range(len(payment_doc.references)):
                            ref_name = payment_doc.references[i].reference_name
                            sale_name = item["SaleName"]
                            if ref_name == sale_name:
                                payment_doc.references.remove(
                                    payment_doc.references[i]
                                )
                        payment_doc.save()
                    return {
                        'success': False,
                        'payments': matched_payments
                    }
        return {'success': True, 'payments': matched_payments}

    @staticmethod
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
            # Check if payment is assignable
            if unallocated_amount > 0:
                # Adjust "Payment Entry Reference" "allocated_amount" if
                # "Payment Entry" "unallocated_amount" is greater then
                # then outstanding amount
                ref_outstanding = reference_details["outstanding_amount"]
                if unallocated_amount > ref_outstanding:
                    reference_details["allocated_amount"] = \
                        ref_outstanding
                else:
                    reference_details["allocated_amount"] = unallocated_amount

                new_row = paymentEntryDoc.append("references")
                new_row.docstatus = 1
                new_row.update(reference_details)

                paymentEntryDoc.flags. \
                    ignore_validate_update_after_submit = True
                paymentEntryDoc.setup_party_account_field()
                paymentEntryDoc.set_missing_values()
                paymentEntryDoc.set_amounts()
                paymentEntryDoc.save()

                paymentEntryDoc.reload()
                if paymentEntryDoc.unallocated_amount == 0:
                    paymentEntryDoc.submit()

                return new_row
            else:
                frappe.msgprint(_(
                    "No unallocated amount found. Please refresh page"
                ))
        except Exception as e:
            frappe.log_error(frappe.get_traceback())
            frappe.throw(_(
                "Could not create payment reference: {0}"
            ).format(e))
            return False
