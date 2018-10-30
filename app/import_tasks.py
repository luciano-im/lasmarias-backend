#-*- coding: utf-8 -*-

import os
import tablib
from django.conf import settings

from app.admin import CustomerResource
from app.admin import ProductsResource


def importCustomer():
    customer_csv = os.path.join(settings.FTP_IMPORT_DIR, 'Clientes.CSV')
    f = open(customer_csv, 'r')
    dataset = tablib.import_set(f.read(), format='csv', delimiter=';', headers=False)
    dataset.headers = ('customer_id','doc_type','cuit','name','address','city','zip_code','email','telephone')

    customer_resource = CustomerResource()
    # Test import
    result = customer_resource.import_data(dataset, dry_run=True)
    # If result has no errors then import (create or update) the data
    if not result.has_errors():
        customer_resource.import_data(dataset, dry_run=False)


def importProducts():
	products_csv = os.path.join(settings.FTP_IMPORT_DIR, 'Productos.CSV')
	f = open(products_csv, 'r')
	dataset = tablib.import_set(f.read(), format='csv', delimiter=';', headers=False)
	dataset.headers = ('id','name','product_line','unit','price')

	products_resource = ProductsResource()
	# Test import
	result = products_resource.import_data(dataset, dry_run=True)
	# If result has no errors then import (create or update) the data
	if not result.has_errors():
		products_resource.import_data(dataset, dry_run=False)
