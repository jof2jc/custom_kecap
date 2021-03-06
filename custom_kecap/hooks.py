# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "custom_kecap"
app_title = "Custom Kecap"
app_publisher = "jonathan"
app_description = "custom kecap"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "jof2jc@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/custom_kecap/css/custom_kecap.css"
# app_include_js = "/assets/custom_kecap/js/custom_kecap.js"


# include js, css files in header of web template
# web_include_css = "/assets/custom_kecap/css/custom_kecap.css"
# web_include_js = "/assets/custom_kecap/js/custom_kecap.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_list_js = {
  "Sales Invoice": "public/js/sales_invoice_list.js"
}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "custom_kecap.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "custom_kecap.install.before_install"
# after_install = "custom_kecap.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "custom_kecap.notifications.get_notification_config"
notification_config = "custom_kecap.custom_kecap.custom_kecap.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {
    "Sales Invoice": {
        "on_submit": "custom_kecap.custom_kecap.custom_kecap.update_ar_status_based_on_last_invoice",
	"on_cancel": "custom_kecap.custom_kecap.custom_kecap.update_ar_status_based_on_last_invoice"
    },
    "Payment Entry": {
        "on_submit": "custom_kecap.custom_kecap.custom_kecap.update_ar_status_after_payment",
	"on_cancel": "custom_kecap.custom_kecap.custom_kecap.update_ar_status_after_payment"
    },
    "Customer": {
	"autoname": "custom_kecap.custom_kecap.custom_kecap.customer_autoname"
	#"on_update": "custom_kecap.custom_kecap.custom_kecap.customer_on_update"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"custom_kecap.tasks.all"
# 	],
# 	"daily": [
# 		"custom_kecap.tasks.daily"
# 	],
# 	"hourly": [
# 		"custom_kecap.tasks.hourly"
# 	],
# 	"weekly": [
# 		"custom_kecap.tasks.weekly"
# 	]
# 	"monthly": [
# 		"custom_kecap.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "custom_kecap.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "custom_kecap.event.get_events"
# }

