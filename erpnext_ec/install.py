import click

import frappe


def before_install():
	print("Setting up ERPNext Ecuador (before_install)...")


def after_install():
	try:
		print("Setting ERPNext Ecuador...")
		click.secho("Thank you for installing ERPNext Ecuador!", fg="green")
	except Exception:
		click.secho(
			"Installation for ERPNext Ecuador app failed due to an error."
			" Please try re-installing the app.",
			fg="bright_red",
		)
		raise
