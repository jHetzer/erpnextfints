# coding=utf-8
from __future__ import unicode_literals

import hashlib
import frappe
from frappe import _


class ImportPaymentEntry:
    def __init__(self, fints_login, interactive, allow_error=False):
        self.allow_error = allow_error
        self.payment_entries = []
        self.fints_login = fints_login
        self.default_customer = fints_login.default_customer
        self.default_supplier = fints_login.default_supplier
        self.interactive = interactive

    def get_party_by_value(self, sender_type, sender, iban=None):
        party_name = None

        if frappe.db.exists(sender_type, sender):
            party_name = frappe.get_value(sender_type, sender, 'name')

        is_default = False
        if not party_name:
            if sender_type == 'Customer':
                party_name = self.default_customer
                is_default = True
            elif sender_type == 'Supplier':
                party_name = self.default_supplier
                is_default = True

        return {'is_default': is_default, 'party': party_name}

    def fints_import(self, fints_transaction):
        # F841 total_items = len(fints_transaction)
        self.interactive.progress = 0
        total_transactions = len(fints_transaction)

        for idx, t in enumerate(fints_transaction):
            # Convert to positive value if required
            amount = abs(float(t['amount']['amount']))
            status = t['status'].lower()
            
            if amount == 0:
                continue

            if status not in ['c', 'd']:
                frappe.log_error(_('Payment type not handled'), _('FinTS Import Error'))
                continue

            if status == 'c' and not self.fints_login.enable_received:
                continue

            if status == 'd' and not self.fints_login.enable_pay:
                continue

            txn_number = idx + 1
            progress = txn_number / total_transactions * 100
            message = _('Query transaction {0} of {1}').format(txn_number, total_transactions)
            self.interactive.show_progress_realtime(message, progress, reload=False)

            # date is in YYYY.MM.DD (json)
            date = t['date']
            applicant_name = t['applicant_name']
            posting_text = t['posting_text']
            purpose = t['purpose']
            applicant_iban = t['applicant_iban']
            applicant_bin = t['applicant_bin']
            
            remarkType = ''
            paid_to = None
            paid_from = None

            uniquestr = ','.join([date, amount, applicant_name, posting_text, purpose])
            transaction_id = hashlib.md5(uniquestr.encode()).hexdigest()
            if frappe.db.exists('Payment Entry', filters={'reference_no': transaction_id}):
                continue

            if status == 'c':
                payment_type = 'Receive'
                party_type = 'Customer'
                paid_to = self.fints_login.erpnext_account  # noqa: E501
                remarkType = 'Sender'
            elif status == 'd':
                payment_type = 'Pay'
                party_type = 'Supplier'
                paid_from = self.fints_login.erpnext_account  # noqa: E501
                remarkType = 'Receiver'

            party = self.get_party_by_value(party_type, applicant_name, applicant_iban)
            if party['is_default']:
                remarks = '{0} "{1}":\n{2} {3}'.format(remarkType, applicant_name, posting_text, purpose)
            else:
                remarks = '{0} {1}'.format(posting_text, purpose)

            payment_entry = frappe.get_doc({
                'doctype': 'Payment Entry',
                'company': self.fints_login.company,
                'paid_amount': amount,
                'received_amount': amount,
                'allocate_payment_amount': 0,
                'reference_no': transaction_id,
                'posting_date': date,
                'reference_date': date,
                'sender': applicant_name,
                'iban': applicant_iban,
                'bic': applicant_bin,
                'payment_type': payment_type,
                'party_type': party_type,
                'paid_to': paid_to,
                'paid_from': paid_from,
                'party': party['party'],
                'remarks': remarks
            })
            payment_entry.insert()
            self.payment_entries.append(payment_entry)
