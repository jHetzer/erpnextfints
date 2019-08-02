// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt

frappe.ui.form.on('FinTS Schedule', {
	refresh: function(frm) {
		frm.clear_custom_buttons();
		frm.events.import_transactions(frm);
	},
	import_transactions: function(frm) {
		frm.add_custom_button(__("Import Transaction"), function(){
			frm.save().then(() => {
				frappe.call({
					method: "erpnextfints.erpnextfints.doctype.fints_schedule.fints_schedule.import_fints_payments",
					args: {
						'manual': true
					}
				});
			});
		}).addClass("btn-primary");
	}
});
