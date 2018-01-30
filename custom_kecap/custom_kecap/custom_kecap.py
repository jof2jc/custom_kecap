from __future__ import unicode_literals
import frappe
from frappe import _

from frappe.utils import nowdate, now_datetime, flt, cstr, formatdate, get_datetime
from frappe.model.naming import make_autoname
import json
import datetime

def sales_person_validate(self, method):
	if not frappe.db.exists("Employee", self.name) and not self.employee:
		emp = frappe.new_doc("Employee")
		emp.employee_name = self.sales_person_name
		emp.save()

		self.employee = emp.name

def item_autoname(self, method):
	self.item_code = self.item_code.strip().upper()
	self.item_name = self.item_code
	self.name = self.item_code

def customer_autoname(self, method):
	abbr = frappe.db.get_value("Territory", self.territory, "abbr")
	initial = self.customer_name[:1]
	self.name = make_autoname(self.customer_name + '-' + abbr.upper() + '-' + initial.upper() +'.###')

	"""
	if self.customer_code.strip() != self.customer_name:
		self.name = self.customer_code.strip().upper() + ' - ' + self.customer_name.strip().upper()
	else:
		self.name = self.customer_code.strip().upper()
	"""

def get_notification_config():
	return {
		"for_doctype": {
			"Sales Invoice": {
				"ar_status": (">", "1"),
				"docstatus": ("<", 2),
				"outstanding_amount": (">", 0)
			}
		}
	}

def set_delivery_status_per_billed(self, method):
	if self.docstatus == 1 or self.docstatus == 2:
		for d in self.items:
			if d.delivery_note:
				ref_doc_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0) from `tabDelivery Note Item`
				where parent=%s""", (d.delivery_note))[0][0])
				print 'ref_doc_qty=' + cstr(ref_doc_qty)
	
				billed_qty = flt(frappe.db.sql("""SELECT ifnull(sum(qty), 0) as billed_qty FROM `tabSales Invoice` si INNER JOIN `tabSales Invoice Item` it 
						ON si.name=it.parent where si.docstatus=1 and it.delivery_note=%s and si.name=%s""", (d.delivery_note, self.name))[0][0])
				#billed_qty = 100
				print 'billed_qty=' + cstr(billed_qty)

				per_billed = ((ref_doc_qty if billed_qty > ref_doc_qty else billed_qty)\
					/ ref_doc_qty)*100
				print 'per_billed=' + cstr(per_billed)

				doc = frappe.get_doc("Delivery Note", d.delivery_note)

				#frappe.throw(_("doc.per_billed = {0} per_billed = {1}").format(doc.per_billed, per_billed))

				if doc.per_billed < 100:
					doc.db_set("per_billed", per_billed)
					doc.set_status(update=True)

				if self.docstatus == 2:
					doc.db_set("per_billed", "0")
					doc.set_status(update=True)

@frappe.whitelist()
def get_dln_rate(item_code, delivery_note):
	return frappe.db.sql('''select rate from `tabDelivery Note Item` dt_item, `tabDelivery Note` dt 
		where dt.name=dt_item.parent and dt.name=%s and dt.docstatus=1 and dt_item.item_code=%s limit 1''', (delivery_note, item_code), as_dict=0)

@frappe.whitelist()
def check_nota_exists(no_nota):
	return frappe.db.sql('''select no_nota from `tabSales Invoice`
		where docstatus=1 and no_nota=%s limit 1''', no_nota, as_dict=0)

@frappe.whitelist()
def get_last_ar_status(customer):
	return frappe.db.sql('''select ar_status from `tabSales Invoice`
		where customer=%s and docstatus=1 Order By ar_status DESC, posting_date ASC, posting_time ASC, name ASC limit 1''', customer, as_dict=0)

@frappe.whitelist()
def get_invoice_ar_status(invoice_no):
	return frappe.db.sql('''select name, ar_status from `tabSales Invoice`
		where name=%s and docstatus=1 Order By posting_date ASC, name ASC limit 1''', invoice_no, as_dict=0)
				
def update_ar_status_after_payment(self, method):
	#si = frappe.get_doc("Purchase Invoice", pi_name)

	if self.payment_type != "Receive" and self.party_type != "Customer":
		return

	if self.docstatus == 2:
		reset_invoices = frappe.db.sql('''SELECT name, ar_status FROM `tabSales Invoice` WHERE docstatus=1 and outstanding_amount > 0 and ar_status >= 0 
		AND customer=%s order by posting_date DESC, posting_time DESC, name DESC''', (self.party), as_dict=1)

		for idx, d in enumerate(reset_invoices):
			si = frappe.get_doc("Sales Invoice", d.name)
			si.ar_status = cstr(idx + 1) #reset over ar_status
			si.save()
		return

	for idx, d in enumerate(self.references):
		si = frappe.get_doc("Sales Invoice", d.reference_name)
		if flt(si.outstanding_amount) == 0:
			si.ar_status = "0"
			si.save()

	outstanding_invoices = frappe.db.sql('''SELECT name, ar_status FROM `tabSales Invoice` WHERE docstatus=1 and outstanding_amount > 0 and ar_status > 0 
		AND customer=%s order by posting_date DESC, posting_time DESC, name DESC''', (self.party), as_dict=1)

	ar_status = 0

	for idx, d in enumerate(outstanding_invoices):
		si = frappe.get_doc("Sales Invoice", d.name)

		ar_status = int(idx) + 1 #restart ar_status
		
		si.ar_status = cstr(ar_status)
		si.save()
		#frappe.throw(_("Expiry date for Batch {0} is {1}").format(d.batch_no, batch_doc.expiry_date))

def update_ar_status_based_on_last_invoice(self, method):
	#si = frappe.get_doc("Purchase Invoice", pi_name)

	set_delivery_status_per_billed(self, method)

	if self.docstatus == 2:
		self.ar_status = "1"
		self.db_set("ar_status", "")
	elif self.docstatus == 1 and self.outstanding_amount == 0:
		self.ar_status = "0"
		self.save()

	invoices = frappe.db.sql('''SELECT name, ar_status FROM `tabSales Invoice` WHERE docstatus=1 and outstanding_amount > 0 and ar_status > 0 
			AND customer=%s and name!=%s order by posting_date DESC, posting_time DESC, ar_status ASC''', (self.customer, self.name), as_dict=1)

	ar_status = 0

	for idx, d in enumerate(invoices):
		si = frappe.get_doc("Sales Invoice", d.name)

		if self.docstatus == 1:
			ar_status = int(si.ar_status) + 1 #increment status
		elif self.docstatus == 2:
			ar_status = int(idx) + 1 #decrement status #reset over
		
		si.ar_status = cstr(ar_status)

		si.save()
		#frappe.throw(_("Expiry date for Batch {0} is {1}").format(d.batch_no, batch_doc.expiry_date))

def update_batch_expiry_status(batch_doc, method):
	#frappe.throw(_("hai"))
	#batch_doc = frappe.get_doc("Batch", self.name)
	days_to_expiry = frappe.utils.date_diff(batch_doc.expiry_date, nowdate())
	batch_doc.days_to_expiry = days_to_expiry

	if int(days_to_expiry) <= int(batch_doc.expiry_start_day) and int(days_to_expiry) > 30:
		batch_doc.expiry_status = "Expired Soon"
	elif int(days_to_expiry) <= 30 and int(days_to_expiry) > 0:
		batch_doc.expiry_status = "Expired Very Soon"
	elif int(days_to_expiry) <= 0:
		batch_doc.expiry_status = "Expired"
	else:
		batch_doc.expiry_status = "Open"

	batch_doc.save()
	#frappe.throw(_("Expiry Status for Batch {0} is {1}").format(self.name, self.expiry_status))

def update_batch_expired_date_daily():
	batch_items = frappe.db.sql ("""SELECT name, item, expiry_date, expiry_start_day FROM `tabBatch`
		where expiry_date <> '' and days_to_expiry >= 0 and expiry_status NOT IN ('Not Set','Expired')""", as_dict=1)

	for d in batch_items:
		if d.expiry_date:
			from erpnext.stock.doctype.batch.batch import get_batch_qty
			batch_qty = get_batch_qty(d.name, "DM Arcadia - MS", None)

			batch_doc = frappe.get_doc("Batch", d.name)
			days_to_expiry = frappe.utils.date_diff(d.expiry_date, nowdate())
			batch_doc.days_to_expiry = days_to_expiry
			
			
			if batch_qty and flt(batch_qty) <= 0:
				batch_doc.expiry_date = nowdate()
				batch_doc.expiry_status	= "Expired"
				batch_doc.days_to_expiry = 0
			elif int(days_to_expiry) <= int(d.expiry_start_day) and int(days_to_expiry) > 30:
				batch_doc.expiry_status	= "Expired Soon"
			elif int(days_to_expiry) <= 30 and int(days_to_expiry) > 0:
				batch_doc.expiry_status	= "Expired Very Soon"
			elif int(days_to_expiry) <= 0:
				batch_doc.expiry_status	= "Expired"
			else:
				batch_doc.expiry_status	= "Open"

			batch_doc.save()

def update_batch_expired_patch():
	batch_items = frappe.db.sql ("""SELECT name, item, expiry_date, expiry_start_day FROM `tabBatch`
		where expiry_status IN ('Expired')""", as_dict=1)

	for d in batch_items:
		if formatdate(d.expiry_date) == "06-09-2017":
			from erpnext.stock.doctype.batch.batch import get_batch_qty
			batch_qty = get_batch_qty(d.name, "DM Arcadia - MS", None)
			#frappe.throw(_("batch qty is {0}").format(batch_qty))
			batch_doc = frappe.get_doc("Batch", d.name)
			#days_to_expiry = frappe.utils.date_diff(d.expiry_date, nowdate())
			#batch_doc.days_to_expiry = days_to_expiry

			if flt(batch_qty) > 0:
				_data = frappe.db.sql ("""SELECT data from `tabVersion` where docname=%s and ref_doctype='Batch' order by modified desc limit 1""", d.name, as_dict=0)
				#frappe.throw(_("{0}").format(_data))
				_data = json.loads(_data[0][0])
				_changes = _data.get("changed")
				#frappe.throw(_("{0}").format(_changes))

				if _changes:
					print(d.name)
					batch_doc.days_to_expiry = _changes[2][1]
					batch_doc.expiry_status	= _changes[0][1]
					batch_doc.expiry_date = get_datetime(formatdate(_changes[1][1]))
				

					batch_doc.save()


def get_expiry_batches(as_list=False):
	"""Returns a count of incomplete todos"""
	#data = frappe.db.sql("""Select count(*) from `tabBatch` where days_to_expiry >= 0""", as_list=True)
	data = frappe.get_list("Batch",
		fields=["name", "days_to_expiry"] if as_list else "count(*)",
		filters=[["Batch", "days_to_expiry", ">=", "0"]],
		as_list=True)

	if as_list:
		return data
	else:
		return data[0][0]
