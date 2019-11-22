// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt

{% include "erpnextfints/public/js/controllers/iban_tools.js" %}

frappe.ui.form.on('Payment Entry', {
  create_party_bank_account: function(frm) {
    erpnextfints.iban_tools.setPartyBankAccount(frm);
  },
  iban: function(frm) {
    // remove error mark if IBAN is valid or field is empty
    if(erpnextfints.iban_tools.isValidIBANNumber(frm.doc.iban) || !frm.doc.iban){
      $('div[data-fieldname="iban"]').removeClass("has-error");
    }else{
      //use timeout to prevent override
      setTimeout(function(){
        $('div[data-fieldname="iban"]').addClass("has-error");
      }, 10);
    }
  },
  bic : function(frm) {
    if(erpnextfints.iban_tools.isValidBic(frm.doc.bic) || !frm.doc.bic){
      $('div[data-fieldname="bic"]').removeClass("has-error");
    }else{
      //use timeout to prevent override
      setTimeout(function(){
        $('div[data-fieldname="bic"]').addClass("has-error");
      }, 10);
    }
  }
});
