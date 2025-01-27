# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import base64

import frappe
from frappe.model.document import Document
from frappe.utils.password import decrypt, encrypt


class FinTSLogin(Document):
    def clear_fints_caches(self):
        self.stored_client_blob = None
        self.stored_dialog_blob = None
        self.stored_tan_blob = None
        self.stored_tan_state_decoupled = None
        self.iban_list = None
        self.account_iban = None

    @property
    def stored_client_blob(self):
        return self.read_crypted_string_to_blob(self.stored_client_state)

    @stored_client_blob.setter
    def stored_client_blob(self, value: bytes):
        self.client_state_updated = frappe.utils.now_datetime() if value else None
        self.stored_client_state = self.conv_blob_to_encrypted_string(value)

    @property
    def stored_dialog_blob(self):
        return self.read_crypted_string_to_blob(self.stored_dialog_state)

    @stored_dialog_blob.setter
    def stored_dialog_blob(self, value: bytes):
        self.dialog_state_updated = frappe.utils.now_datetime() if value else None
        self.stored_dialog_state = self.conv_blob_to_encrypted_string(value)

    @property
    def stored_tan_blob(self):
        return self.read_crypted_string_to_blob(self.stored_tan_state)

    @stored_tan_blob.setter
    def stored_tan_blob(self, value: bytes):
        self.tan_state_updated = frappe.utils.now_datetime() if value else None
        self.stored_tan_state = self.conv_blob_to_encrypted_string(value)

    def read_crypted_string_to_blob(self, encoded_encrypted_string: str) -> bytes | None:
        """Decrypts ascii base64, and decrypts result to return blob"""
        if not encoded_encrypted_string:
            return None

        # decrypt to base64 string
        blob_str = decrypt(encoded_encrypted_string)

        # decode base64 string to blob
        return base64.b64decode(blob_str)

    def conv_blob_to_encrypted_string(self, blob: bytes) -> str | None:
        """Encrypts blob, and converts to ascii base64"""
        if not blob:
            return None

        # convert blob to base64 string
        blob_str = base64.b64encode(blob).decode()

        # encrypt the base64-blob-string
        return encrypt(blob_str)

    @frappe.whitelist(allow_guest=False)
    def reset_connection(self):
        frappe.has_permission(ptype="write", doc=self, throw=True)
        self.clear_fints_caches()
        self.save()

    # TODO
    # @frappe.whitelist(allow_guest=False)
    # def solve_tan_challenge(self, tan: str | None=''):
    #     """
    #     If a tan was requested in a background task or some other previous status, the socket prompt might not have
    #     been shown. This method allows to trigger the challenge again to solve it.
    #     """
    #     frappe.has_permission(ptype="write", doc=self, throw=True)

    #     from erpnextfints.utils.fints_controller import FinTSController

    #     # Just init the FintsController instance should be enough to check for a tan challenge and make it continue:
    #     # TAN will be requested via socket communication during initialization time.
    #     FinTSController(self.name, {"docname": self.name, "enabled": True})
