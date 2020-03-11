// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt

{% include "erpnextfints/public/js/controllers/iban_tools.js" %}

frappe.ui.form.on('Payment Entry', {
	onload: function(frm) {
		getBankAccountPermission(frm);
	},
	create_party_bank_account: function(frm) {
		erpnextfints.iban_tools.setPartyBankAccount(frm);
	},
	paid_from: function(frm) {
		hideBanlAccountButton(frm);
	},
	paid_to: function(frm) {
		hideBanlAccountButton(frm);
	},
	party: function(frm) {
		hideBanlAccountButton(frm);
	},
	sender: function(frm) {
		hideBanlAccountButton(frm);
	},
	iban: function(frm) {
		// remove error mark if IBAN is valid or field is empty
		if(erpnextfints.iban_tools.isValidIBANNumber(frm.doc.iban) || !frm.doc.iban){
			$('div[data-fieldname="iban"]').removeClass("has-error");
			hideBanlAccountButton(frm);
		}else{
			// use timeout to prevent override
			setTimeout(function(){
				$('div[data-fieldname="iban"]').addClass("has-error");
				frm.toggle_display("create_party_bank_account",false);
			}, 10);
		}
	},
	bic : function(frm) {
		if(erpnextfints.iban_tools.isValidBic(frm.doc.bic) || !frm.doc.bic){
			$('div[data-fieldname="bic"]').removeClass("has-error");
		}else{
			// use timeout to prevent override
			setTimeout(function(){
				$('div[data-fieldname="bic"]').addClass("has-error");
			}, 10);
		}
	}
});

var hideBanlAccountButton = function(frm) {
	frm.toggle_display(
		"create_party_bank_account",
		frm.doc.hasBankAccountPermission
	);
};

var getBankAccountPermission = function(frm) {
	frappe.call({
		method: "erpnextfints.utils.client.has_page_permission",
		args: {
			page_name: 'bank_account_wizard'
		},
		callback: function(result){
			frm.doc.hasBankAccountPermission = result.message;
			hideBanlAccountButton(frm);
		}
	});
};
