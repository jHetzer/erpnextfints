// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt

frappe.provide("erpnextfints.interactive");

erpnextfints.interactive = {
	updateQueue: Promise.resolve(),

	enqueueUpdate: function(fn, delay) {
		this.updateQueue = this.updateQueue
			.then(() => {
				// call the function
				return Promise.resolve(fn());
			})
			.then(() => {
				// delay the next update
				return new Promise((resolve) => setTimeout(resolve, delay || 500));
			});

		return this.updateQueue;
	},

	progressbar: function(frm) {
		frappe.realtime.off("fints_progressbar");
		frappe.realtime.on("fints_progressbar", function(data) {
			if(data.docname === frm.doc.name) {

				erpnextfints.interactive.enqueueUpdate(() => {
					if(data.progress==100) {
						frappe.hide_progress();
					} else {
						frappe.show_progress(data.docname,data.progress,100,data.message);
					}

					if(data.reload && data.reload === true) {
						// reload with short delay, to have progress update come active before
						erpnextfints.interactive.enqueueUpdate(() => {
							frm.reload_doc()
						}, 500);
					}
				});
			}
		});

		/**
		 * Handle TAN interaction requirements for several steps:
		 * 1. TAN Mode selection
		 * 1.2. TAN Medium selection (if available)
		 * 2. Later User Interaction after Push TAN fulfillment or TAN entered
		 */
		frappe.realtime.off("fints_tan_interaction_required");
		frappe.realtime.on("fints_tan_interaction_required", async function(data) {
			if(data.docname !== frm.doc.name) {
				return;
			}

			await erpnextfints.interactive.enqueueUpdate(() => {
				frappe.hide_progress();
			});

			let fields = [];

			if (data.possible_tan_modes) {
				fields.push(
					{
						fieldtype: "Select",
						fieldname: "tan_mode",
						label: __("TAN Mode"),
						options: data.possible_tan_modes,
						reqd: 1,
					},
				);

				if (data.possible_tan_mediums) {
					// if mediums are available for the selected mode, keep previously selected mode read-only
					fields[0].default = data.possible_tan_modes[0];
					fields[0].read_only = 1;

					fields.push(
						{
							fieldtype: "Select",
							fieldname: "tan_medium",
							label: __("TAN Medium"),
							options: data.possible_tan_mediums,
							reqd: 1,
						},
					);
				}
			}

			// TAN Mode selection
			if (data.tan_required || data.mfa_required) {
				if (data.possible_tan_modes && !fields[0].default) {
					fields[0].default = data.possible_tan_modes[0];
					fields[0].read_only = 1;
				}

				// if we're on confirmation already, keep previously selected mode read-only
				if (data.possible_tan_mediums) {
					const disableIdx = data.possible_tan_mediums ? 1 : 0;
					fields[disableIdx].default = data.possible_tan_mediums[disableIdx];
					fields[disableIdx].read_only = 1;
				}

				// User Interaction requirement for 2FA
				fields.push(
					{
						fieldtype: "Check",
						fieldname: "mfa_confirmation",
						label: __("Confirm MFA"),
						default: 1,
						hidden: 1,
					},
				);

				if (data.tan_required) {
					fields.push(
						{
							fieldtype: "Data",
							fieldname: "tan",
							label: __("TAN"),
							reqd: 1,
						},
					);
				} else if (data.mfa_required) {
					fields.push(
						{
							fieldtype: "HTML",
							fieldname: "waiting",
							label: __("Waiting for Interaction"),
							options: __("Follow the instructions on your banking app or device."),
						},
					);
				}
			}

			frappe.prompt(
				fields,
				(values) => {
					frappe.call({
						method: "erpnextfints.utils.client.resolve_tan_interaction",
						args: {
							fints_login: frm.doc.name,
							values: { ...data, ...values },
						},
					});
				},
				__("Verification required")
			);
		});
	},
}
