# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import frappe, os, json
from frappe import _

cur_dir = os.path.dirname(__file__)

@frappe.whitelist()
def createBankAccount(payment_doc, bankData):
    try:
        payment_doc = json.loads(payment_doc)
        bankData = json.loads(bankData)

        if not frappe.db.exists('Bank', {'bank_name': bankData.get('name')}):
            frappe.get_doc({
              'doctype': 'Bank',
              'bank_name': bankData.get('name')
            }).submit()
        gl_account = None
        if payment_doc.get('payment_type') == "Pay":
            gl_account = payment_doc.get('paid_from')
        else:
            gl_account = payment_doc.get('paid_to')

        bankAccount = {
          'doctype': 'Bank Account',
          'account_name': payment_doc.get('sender'),
          'account': gl_account,
          'bank': bankData.get('name'),
          'party_type': payment_doc.get('party_type'),
          'party': payment_doc.get('party'),
          'iban': payment_doc.get('iban'),
          'bank_account_no': bankData.get('64061854'),
          'swift_number': bankData.get('bic'),
          'is_company_account': False,
          'is_default': False,
        }
        if not frappe.db.exists('Bank Account', (
            payment_doc.get('sender') + " - " + bankData.get('name'))
        ):
            newBankAccount = frappe.get_doc(bankAccount)
            newBankAccount.submit()
            frappe.msgprint(_("Successfully created Bank Account"))
            return newBankAccount
        else:
            frappe.msgprint(_("Bank account already exists"))
            return True
    except Exception as e:
        frappe.throw(_("Could not create bank account with error: {0}").format(e))

@frappe.whitelist()
def getPossibleBankAccount():
    file_path = os.path.join(cur_dir, './sql/bank_wizard.sql')
    filehandle = open(file_path)
    sqlQuery = filehandle.read()
    filehandle.close()
    return frappe.db.sql(sqlQuery, as_dict=True)
