#-*- coding: utf-8 -*-

import os
from datetime import datetime
import tablib
from django.conf import settings

from app.admin import CustomerResource
from app.admin import ProductsResource

from app.models import CSVFilesData


def importCustomer():
    customer_csv = os.path.join(settings.FTP_IMPORT_DIR, 'Clientes.CSV')

    try:
        mtime = os.path.getmtime(customer_csv)
        last_modified_date = datetime.fromtimestamp(mtime)
    except OSError:
        mtime = 0

    file_data = CSVFilesData.objects.get(file='clientes')

    print(last_modified_date)
    print(file_data.modified_date)

    if file_data.modified_date != last_modified_date:
        print('ACTUALIZO BASE DE CLIENTES')
        file_data.modified_date = last_modified_date
        file_data.save()

        f = open(customer_csv, 'r')
        dataset = tablib.import_set(f.read(), format='csv', delimiter=';', headers=False)
        dataset.headers = ('customer_id','doc_type','cuit','name','address','city','zip_code','email','telephone')

        customer_resource = CustomerResource()
        # Test import
        result = customer_resource.import_data(dataset, dry_run=True)
        # If result has no errors then import (create or update) the data
        if not result.has_errors():
            customer_resource.import_data(dataset, dry_run=False)
    else:
        print('NO ACTUALIZO BASE DE CLIENTES')


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
