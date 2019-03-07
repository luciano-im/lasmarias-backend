#-*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from app import import_tasks

class Command(BaseCommand):
	help = 'Import Account Balance database table'

	def handle(self, *args, **options):
		try:
			import_tasks.importAccountBalance()
			self.stdout.write(self.style.SUCCESS('Successfully updated Account Balance'))
		except:
			self.stdout.write(self.style.ERROR('Could not update Account Balance'))
