from __future__ import unicode_literals

from frappe import _
import frappe
import hashlib


class ImportPaymentEntry:
    def __init__(self, fints_login, interactive, allow_error=False):
        self.allow_error = allow_error
        self.payment_entries = []
        self.fints_login = fints_login
        self.default_customer = fints_login.default_customer
        self.default_supplier = fints_login.default_supplier
        self.interactive = interactive

    def get_party_by_value(self, sender, party_type, iban=None):
        party = None
        is_default = False
        party_name = frappe.get_value(party_type, sender, 'name')

        if iban:
            '''
            iban_sql_query = ("SELECT `name` " +
                        "FROM `tab{0}` " +
                        "WHERE `iban` = '{1}'").format(party_type, iban)
            '''
            iban_sql_query = (
                "SELECT "
                "`name`, `iban`, `party`, `party_type` "
                "FROM `tabBank Account` "
                "WHERE `party_type` = '{0}' "
                "AND `iban` = '{1}' "
                "AND `party` IS NOT NULL;").format(party_type, iban)
            party_by_iban = frappe.db.sql(iban_sql_query, as_dict=True)
            if len(party_by_iban) == 1:
                party = party_by_iban[0].party
        if not party and party_name:
            party = party_name
        if not party:
            "party"
            if party_type == "Customer":
                party = self.default_customer
            elif party_type == "Supplier":
                party = self.default_supplier
            is_default = True

        return {"is_default": is_default, "party": party}

    def fints_import(self, fints_transaction):
        # F841 total_items = len(fints_transaction)
        remarkType = ""
        self.interactive.progress = 0
        total_transaction = len(fints_transaction)
        for idx, t in enumerate(fints_transaction):
            self.interactive.show_progress_realtime(
                _("Query transcation {0} of {1}").format(
                    idx + 1,
                    total_transaction
                ),
                (idx + 1) / total_transaction * 100,
                reload=False
            )
            if float(t["amount"]["amount"]) != 0:
                # Convert to positive value if required
                amount = abs(float(t["amount"]["amount"]))

                partyMapping = t["applicant_name"]
                uniquestr = "{0},{1},{2},{3},{4}".format(
                    t["date"],
                    amount,
                    partyMapping,
                    t["posting_text"],
                    t['purpose']
                )
                transaction_id = hashlib.md5(
                    uniquestr.encode('utf-8')
                ).hexdigest()
                if not frappe.db.exists(
                    'Payment Entry', {
                        'reference_no': transaction_id
                    }
                ):
                    # date is in YYYY.MM.DD (json)
                    new_payment_entry = frappe.get_doc({
                        'doctype': 'Payment Entry',
                        'allocate_payment_amount': 0,
                        'reference_no': transaction_id,
                        'posting_date': t["date"],
                        'reference_date': t["date"],
                        'company': self.fints_login.company,
                        'paid_amount': amount,
                        'received_amount': amount,
                        'iban': t["applicant_iban"],
                        'sender': t["applicant_name"],
                        'bic': t["applicant_bin"]
                    })
                    if t["status"].lower() == "c":
                        if self.fints_login.enable_received:
                            new_payment_entry.payment_type = "Receive"
                            new_payment_entry.party_type = "Customer"
                            new_payment_entry.paid_to = self.fints_login.erpnext_account  # noqa: E501
                            remarkType = "Sender"
                        else:
                            continue
                    elif t["status"].lower() == "d":
                        if self.fints_login.enable_pay:
                            new_payment_entry.payment_type = "Pay"
                            new_payment_entry.party_type = "Supplier"
                            new_payment_entry.paid_from = self.fints_login.erpnext_account  # noqa: E501
                            remarkType = "Receiver"
                        else:
                            continue
                    else:
                        frappe.log_error(
                            _("Payment type not handled"),
                            _("FinTS Import Error")
                        )
                        continue

                    party = self.get_party_by_value(
                        t["applicant_name"],
                        new_payment_entry.party_type,
                        t["applicant_iban"]
                    )
                    new_payment_entry.party = party["party"]
                    if party["is_default"]:
                        remarks = ("{0} '{1}':\n{2} {3}").format(
                            remarkType,
                            t["applicant_name"],
                            t["posting_text"],
                            t['purpose']
                        )
                    else:
                        remarks = "{0} {1}".format(
                            t["posting_text"],
                            t['purpose']
                        )
                    new_payment_entry.remarks = remarks

                    self.payment_entries.append(new_payment_entry.insert())
