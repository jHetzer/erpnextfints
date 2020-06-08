// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt

frappe.provide("erpnextfints.interactive");

erpnextfints.interactive = {
	progressbar: function(frm) {
		let ajaxErrorCloseHandler = function(/* e */){
			// Queue close function on ajax error
			setTimeout(function(){
				frappe.hide_progress();
			},2000);
		};
		let pageUnloadHandler = function(){
			$(document).unbind("ajaxError",ajaxErrorCloseHandler);
			setTimeout(function(){
				// Queue unbind action on page leave
				$(document).unbind("form-unload",pageUnloadHandler);
			},0);
		};
		frappe.ui.form.on(frm.doc.doctype, {
			refresh: function() {
				$(document).ajaxError(ajaxErrorCloseHandler);
			}
		});
		$(document).on("form-unload", pageUnloadHandler);

		frappe.realtime.on("fints_progressbar", function(data) {
			if(data.docname === frm.doc.name) {
				if(data.reload && data.reload === true) {
					frm.reload_doc();
				}
				if(data.progress === 100) {
					frappe.hide_progress();
				} else {
					frappe.show_progress(data.docname,data.progress,100,data.message);
				}
			}
		});
	},
};
