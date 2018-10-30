#-*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from app import import_tasks

class Command(BaseCommand):
	help = 'Import Customer database table'

	def handle(self, *args, **options):
		try:
			import_tasks.importCustomer()
			self.stdout.write(self.style.SUCCESS('Successfully updated Customer'))
		except:
			self.stdout.write(self.style.ERROR('Could not update Customer'))
