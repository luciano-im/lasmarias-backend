#-*- coding: utf-8 -*-

import os
from datetime import datetime
import tablib

from django.conf import settings
from django.db.models import Q

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.exceptions import PubNubException

from app.admin import CustomerResource
from app.admin import ProductsResource
from app.admin import AccountBalanceResource
from app.admin import InvoicesResource
from app.admin import InvoiceItemsResource

from app.models import CSVFilesData


def PublishUpdate():
    pnconfig = PNConfiguration()
    pnconfig.publish_key = settings.PUBNUB_PUBLISH_KEY
    pnconfig.subscribe_key = settings.PUBNUB_SUBSCRIBE_KEY
    pnconfig.ssl = False
    pubnub = PubNub(pnconfig)

    def publish_callback(result, status):
        print(result)
        print(status)
        # Handle PNPublishResult and PNStatus
 
    try:
        publish_data = list(CSVFilesData.objects.filter(Q(file='Productos') | Q(file='Clientes')).values('file', 'modified_date'))
        pubnub.publish().channel('lasmarias').message(publish_data).pn_async(publish_callback)
    except PubNubException as e:
        print(e)


def importCustomer():
    customer_csv = os.path.join(settings.FTP_IMPORT_DIR, 'Clientes.CSV')

    try:
        # Get modified date/time
        mtime = os.path.getmtime(customer_csv)
        last_modified_date = datetime.fromtimestamp(mtime)
    except OSError:
        mtime = 0

    file_data = CSVFilesData.objects.get(file='Clientes')

    # Update if modified date/time has changed
    if file_data.modified_date != str(last_modified_date):
        print('ACTUALIZO BASE DE CLIENTES')

        f = open(customer_csv, 'r')
        dataset = tablib.import_set(f.read(), format='csv', delimiter=';', headers=False)
        dataset.headers = ('customer_id','doc_type','cuit','name','address','city','telephone','discount')

        customer_resource = CustomerResource()
        # Test import
        result = customer_resource.import_data(dataset, dry_run=True)
        # If result has no errors then import (create or update) the data
        if not result.has_errors():
            customer_resource.import_data(dataset, dry_run=False)
            file_data.modified_date = last_modified_date
            file_data.save()

            PublishUpdate()

    else:
        print('NO ACTUALIZO BASE DE CLIENTES')


def importProducts():
    products_csv = os.path.join(settings.FTP_IMPORT_DIR, 'Productos.CSV')

    try:
        # Get modified date/time
        mtime = os.path.getmtime(products_csv)
        last_modified_date = datetime.fromtimestamp(mtime)
    except OSError:
        mtime = 0

    file_data = CSVFilesData.objects.get(file='Productos')

    # Update if modified date/time has changed
    if file_data.modified_date != str(last_modified_date):
        print('ACTUALIZO BASE DE PRODUCTOS')
        
        f = open(products_csv, 'r')
        dataset = tablib.import_set(f.read(), format='csv', delimiter=';', headers=False)
        dataset.headers = ('product_id','name','brand','product_line','unit','price','offer','offer_price','package')

        products_resource = ProductsResource()
        # Test import
        result = products_resource.import_data(dataset, dry_run=True)
        # If result has no errors then import (create or update) the data
        if not result.has_errors():
            products_resource.import_data(dataset, dry_run=False)
            file_data.modified_date = last_modified_date
            file_data.save()

            PublishUpdate()
    else:
        print('NO ACTUALIZO BASE DE PRODUCTOS')


def importAccountBalance():
    account_csv = os.path.join(settings.FTP_IMPORT_DIR, 'CompSaldos.CSV')

    try:
        # Get modified date/time
        mtime = os.path.getmtime(account_csv)
        last_modified_date = datetime.fromtimestamp(mtime)
    except OSError:
        mtime = 0

    file_data = CSVFilesData.objects.get(file='CompSaldos')

    # Update if modified date/time has changed
    if file_data.modified_date != str(last_modified_date):
        print('ACTUALIZO SALDOS DE CUENTA CORRIENTE')
        
        f = open(account_csv, 'r')
        dataset = tablib.import_set(f.read(), format='csv', delimiter=';', headers=False)
        dataset.headers = ('customer_id','date','voucher','balance')

        account_resource = AccountBalanceResource()
        # Test import
        result = account_resource.import_data(dataset, dry_run=True)
        # If result has no errors then import (create or update) the data
        if not result.has_errors():
            account_resource.import_data(dataset, dry_run=False)
            file_data.modified_date = last_modified_date
            file_data.save()
    else:
        print('NO ACTUALIZO SALDOS DE CUENTA CORRIENTE')


def importInvoices():
    invoice_header_csv = os.path.join(settings.FTP_IMPORT_DIR, 'Comprobantes.CSV')
    invoice_items_csv = os.path.join(settings.FTP_IMPORT_DIR, 'Comp_Items.CSV')

    try:
        # Get modified date/time
        header_mtime = os.path.getmtime(invoice_header_csv)
        items_mtime = os.path.getmtime(invoice_items_csv)
        header_last_modified_date = datetime.fromtimestamp(header_mtime)
        items_last_modified_date = datetime.fromtimestamp(items_mtime)
    except OSError:
        header_mtime = 0
        items_mtime = 0

    file_header_data = CSVFilesData.objects.get(file='Comprobantes')
    file_items_data = CSVFilesData.objects.get(file='Comp_Items')

    # Update if modified date/time has changed
    if file_header_data.modified_date != str(header_last_modified_date):
        print('ACTUALIZO CABECERA DE FACTURAS')
        
        f = open(invoice_header_csv, 'r')
        dataset = tablib.import_set(f.read(), format='csv', delimiter=';', headers=False)
        dataset.headers = ('customer_id','invoice_type','invoice_branch','invoice_number','date','iva','taxes')

        invoice_header_resource = InvoicesResource()
        # Test import
        result = invoice_header_resource.import_data(dataset, dry_run=True)
        # If result has no errors then import (create or update) the data
        if not result.has_errors():
            invoice_header_resource.import_data(dataset, dry_run=False)
            # file_header_data.modified_date = header_last_modified_date
            # file_header_data.save()
    else:
        print('NO ACTUALIZO CABECERA DE FACTURAS')
    
    if file_items_data.modified_date != str(items_last_modified_date):
        print('ACTUALIZO ITEMS DE FACTURAS')
        
        f = open(invoice_items_csv, 'r')
        dataset = tablib.import_set(f.read(), format='csv', delimiter=';', headers=False)
        dataset.headers = ('invoice_type','invoice_branch','invoice_number','product_id','price','quantity','amount','product_description')

        invoice_items_resource = InvoiceItemsResource()
        # Test import
        result = invoice_items_resource.import_data(dataset, dry_run=True)
        # If result has no errors then import (create or update) the data
        if not result.has_errors():
            invoice_items_resource.import_data(dataset, dry_run=False)
            # file_items_data.modified_date = items_last_modified_date
            # file_items_data.save()
    else:
        print('NO ACTUALIZO ITEMS DE FACTURAS')

