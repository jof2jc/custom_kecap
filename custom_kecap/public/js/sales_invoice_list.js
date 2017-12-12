/* frappe.listview_settings['Batch'] = {
	add_fields: ["expiry_status"],
	get_indicator: function (doc) {
		return [__(doc.expiry_status), {
			"Expired": "grey",
			"Expired Soon": "orange",
			"Expired Very Soon": "red",
			"Open": "green",
			"Not Set": "darkgrey",
		}[doc.expiry_status], "expiry_status,=," + doc.expiry_status];
	}

};
// render
frappe.listview_settings['Sales Invoice'] = {
	add_fields: ["customer", "customer_name", "base_grand_total", "outstanding_amount", "due_date", "company",
		"currency", "is_return"],
	get_indicator: function(doc) {
		if(cint(doc.is_return)==1) {
			return [__("Return"), "darkgrey", "is_return,=,Yes"];
		} else if(flt(doc.outstanding_amount)==0) {
			return [__("Paid"), "green", "outstanding_amount,=,0"]
		} else if(flt(doc.outstanding_amount) < 0) {
			return [__("Credit Note Issued"), "darkgrey", "outstanding_amount,<,0"]
		}else if (flt(doc.outstanding_amount) > 0 && doc.due_date >= frappe.datetime.get_today()) {
			return [__("Unpaid"), "orange", "outstanding_amount,>,0|due_date,>,Today"]
		} else if (flt(doc.outstanding_amount) > 0 && doc.due_date < frappe.datetime.get_today()) {
			return [__("Overdue"), "red", "outstanding_amount,>,0|due_date,<=,Today"]
		}
	},
	right_column: "grand_total"
};

*/
// render
frappe.listview_settings['Sales Invoice'] = {
	add_fields: ["customer","ar_status", "base_grand_total", "outstanding_amount", "company"],
	get_indicator: function(doc) {
		if(flt(doc.outstanding_amount)==0) {
			return [__("Paid"), "green", "outstanding_amount,=,0"];
		} else if(cint(doc.ar_status) == 1) {
			return [__("First"), "blue", "outstanding_amount,>,0"];
		} else if(cint(doc.ar_status) == 2) {
			return [__("Second"), "yellow", "outstanding_amount,>,0"];
		} else if(cint(doc.ar_status) == 3) {
			return [__("Third"), "orange", "outstanding_amount,>,0"];
		} else if(cint(doc.ar_status) == 4) {
			return [__("Fourth"), "red", "outstanding_amount,>,0"];
		} else if(cint(doc.ar_status) > 4) {
			return [__("Over Delivery - " + doc.ar_status), "red", "outstanding_amount,>,0"];
		}
	},
	right_column: "outstanding_amount"
};