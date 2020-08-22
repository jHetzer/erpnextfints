// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt

{% include "erpnextfints/public/js/controllers/fints_interactive.js" %}

frappe.ui.form.on('FinTS Import', {
	onload: function(frm) {
		erpnextfints.interactive.progressbar(frm);
		if(frm.doc.docstatus == 1){
			frm.toggle_display("import_transaction",false);
			frm.toggle_display("import_details_section",true);
		}
		if(frm.doc.docstatus == 0 && !(frm.doc.to_date)){
			frm.set_value(
				"to_date",
				frappe.datetime.add_days(frappe.datetime.nowdate(),-1)
			);
		}
	},
	/* setup: function(frm) {
		frm.set_value(
			"to_date",
			frappe.datetime.add_days(frappe.datetime.nowdate(),-1)
		);
	},*/
	refresh: function(frm) {
		if(cur_frm.doc.__islocal == null){
			frm.toggle_display("import_transaction",true);
			if(frm.doc.fints_login && frm.doc.docstatus == 0){
				frm.page.set_primary_action(__("Start Import"), function() {
					frm.events.call_import_transaction(frm);
				}).addClass('btn btn-primary');
				frm.page.set_secondary_action(__("Save"), function() {
					frm.save();
				});
			}
		}else{
			frm.toggle_display("import_transaction",false);
		}
	},
	fints_login: function(frm) {
		if(frm.doc.fints_login){
			frm.save();
		}
	},
	from_date: function(frm) {
		if(frm.doc.fints_login){
			if(frm.doc.from_date){
				frm.save();
			}
		}
	},
	to_date: function(frm) {
		if(frm.doc.fints_login){
			if(frm.doc.to_date){
				frm.save();
			}
		}
	},
	import_transaction: function(frm){
		// frappe.show_progress(frm.docname,1,100,"Connect via FinTS")
		frm.events.call_import_transaction(frm);
		/*
		if (frm.doc.__unsaved){
			frm.save().then(() => {
				frm.events.call_import_transaction(frm);
			})
		}else{
			frm.events.call_import_transaction(frm);
			//frappe.hide_progress();
		}
		*/

	},
	call_import_transaction: function(frm){
		// frappe.show_progress(frm.docname,1,100,"Connect via FinTS")
		frappe.call({
			method:"erpnextfints.utils.client.import_fints_transactions",
			args: {
				'fints_import': frm.docname,
				'fints_login': frm.doc.fints_login,
				'user_scope': frm.docname,
			},
			callback: function(/* r */) {
				frappe.hide_progress();
				frm.reload_doc();
			}
		});
	}
});
