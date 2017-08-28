import csv
import os

from django.core.management import BaseCommand
from django.utils.text import slugify

from contacts.models import Organization, ContactGroup, PhoneNumber

__author__ = 'Jonathan Senecal <jsenecal@zerofail.com>'


class Command(BaseCommand):
    args = '<filename>'
    help = "Imports the contacts from the supplied QuickBooks export file"

    @classmethod
    def utf_8_encoder(cls, unicode_csv_data):
        for line in unicode_csv_data:
            yield line.encode('utf-8')

    @classmethod
    def unicode_csv_reader(cls, unicode_csv_data, dialect, **kwargs):
        # csv.py doesn't do Unicode; encode temporarily as UTF-8:
        csv_reader = csv.DictReader(unicode_csv_data, dialect=dialect, **kwargs)
        for row in csv_reader:
            # decode UTF-8 back to Unicode, cell by cell:
            yield dict([(key, value) for key, value in row.items()])

    def handle(self, *args, **options):
        if len(args) == 0:
            self.stderr.write("A filename must be specified")
            return
        elif len(args) != 1:
            self.stderr.write("Only one filename can be specified")
            return
        else:

            # create the file path
            filename = str(args[0])
            # check to make sure its a file not a sub folder
            if os.path.isfile(filename) and filename.endswith(".csv"):

                self.stdout.write("Parsing {:}".format(filename))

                with open(filename, 'r', encoding="ISO-8859-1") as csvfile:
                    # sniff to find the format
                    filedialect = csv.Sniffer().sniff(csvfile.read(1024))
                    csvfile.seek(0)
                    # read the CSV file into a dictionary
                    dictreader = self.unicode_csv_reader(csvfile, dialect=filedialect)
                    for row in dictreader:
                        self.stdout.write(u"Processing {:}".format(row['Customer']))

                        if slugify(row['Company']) == slugify(row['Customer']):
                            org_name = row['Company'].strip()
                            org, created = self.get_or_create_org(org_name)
                        elif slugify(row['Company']) in slugify(row['Customer']) and ":" in row['Customer']:
                            org_name = row['Customer'].split(':')[1].strip()
                            reseller_org_name = row['Customer'].split(':')[0]
                            try:
                                reseller_org = Organization.objects.get(name=reseller_org_name)
                            except Organization.DoesNotExist:
                                self.stderr.write(
                                    "Unable to find a reseller organization named {:}".format(reseller_org_name)
                                )
                                continue
                            org, created = self.get_or_create_org(org_name, reseller_org)
                        else:
                            if len(row['Company']) > 0:
                                org_name = row['Company'].strip()
                            else:
                                org_name = row['Customer'].strip()
                            org, created = self.get_or_create_org(org_name)

                        try:
                            if (not org.resellers) and (row['Main Phone']):
                                cleaned_number, extension = PhoneNumber.phone_number_cleaner(row['Main Phone'])
                                self.stdout.write(u"Adding phone number: {:}".format(cleaned_number))
                                PhoneNumber.objects.get_or_create(
                                    organization=org,
                                    phone_number=cleaned_number,
                                    information_type='company'
                                )
                        except KeyError:
                            pass

                        if created:
                            self.stdout.write(u"Created {:}".format(org))
                        else:
                            self.stdout.write(u"Updated {:}".format(org))

            else:
                self.stderr.write("The file {:} does not exist or is not a .csv".format(filename))

    @staticmethod
    def get_or_create_org(org_name, reseller_org=None):
        org, created = Organization.objects.get_or_create(
            name=org_name
        )

        org.save()
        if reseller_org:
            org.resellers.add(reseller_org)
            group = ContactGroup.objects.language('en').get(id=4)
            group.organizations.add(reseller_org)
            group.save()

        group = ContactGroup.objects.language('en').get(id=5)
        group.organizations.add(org)
        group.save()

        return org, created
