#-*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from app import import_tasks

class Command(BaseCommand):
	help = 'Import Products database table'

	def handle(self, *args, **options):
		try:
			import_tasks.importProducts()
			self.stdout.write(self.style.SUCCESS('Successfully updated Products'))
		except:
			self.stdout.write(self.style.ERROR('Could not update Products'))
