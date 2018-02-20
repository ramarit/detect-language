# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import pyexcel as pe
import os
from os.path import basename
from langdetect import detect
from langdetect import DetectorFactory
import progressbar
from googletrans import Translator

DetectorFactory.seed = 0
translator = Translator()
bar = progressbar.ProgressBar()

output = pe.get_sheet(file_name="contentValidation.xlsx")

# excel spread sheet with NID and PID
# create dictionary from the NID and PID column
records = pe.get_sheet(file_name="id.xlsx")
nid = []
pid = []
for row in records:
	nid.append(str(row[0]))
	if not row[2]:
		pid.append('none')
	else:
		pid.append(str(row[2]))
dictionary = dict(zip(nid, pid))

# path to live products XML file
path = '/Users/ramarit/Desktop/Stash/product-content-validation/Live Products'
# create list of live product NIDs
live_NID = []
for filename in os.listdir(path):
	if not filename.endswith('.xml'):continue
	fullname = os.path.join(path, filename)
	print(fullname)
	with open(fullname) as live:
		live = BeautifulSoup(live, 'xml')
		for product_status in live.findAll('id'):
			live_NID.append(str(product_status.contents[0]))

		# get locale from live products file to open corresponding ECM product export
		locale = filename[:5]
		exportFile = f'/Users/ramarit/Desktop/Stash/product-content-validation/Exports/{locale}_product_display_content_export.xml'
		with open(exportFile) as export:
			export = BeautifulSoup(export, 'xml')
			for entity in export.findAll('entity'):
				nodeID = str(entity.find('id').contents[0])
				if nodeID in live_NID:
					PID = str(dictionary.get(str(nodeID), None))
					locale = str(entity.find('locale').get('value'))

					###### features section ######
					if entity.find('field_features') is None:
						detectFeatures = 'blank'
					else:
						try:
							features = BeautifulSoup(entity.find('field_features').contents[0], 'html.parser').get_text()
							detectFeatures = detect(features)
							if detectFeatures != locale[:2]:
								detectFeatures = str(translator.detect(features).lang)
						except:
							detectFeatures = 'unknown'

					###### overview section ######
					if entity.find('field_overview') is None:
						detectOverview = 'blank'
					else:
						try:	
							overview = BeautifulSoup(entity.find('field_overview').contents[0], 'html.parser').get_text()
							detectOverview = detect(overview)
							if detectOverview != locale[:2]:
								detectOverview = str(translator.detect(overview).lang)
						except:
							detectOverview = 'unknown'

					###### speciication table section ######
					if entity.find('field_specs') is None:
						detectSpecs = 'blank'
					else:
						try:
							specs = BeautifulSoup(entity.find('field_specs').contents[0], 'html.parser').get_text()
							detectSpecs = detect(specs)
							if detectSpecs != locale[:2]:
								detectSpecs = str(translator.detect(specs).lang)
						except:
							detectSpecs = 'unknown'

					###### short description summary section ######
					if entity.find('field_short_description_summary') is None:
						detect_short_description = "blank"
						# short_description = ""
					else:
						try:
							short_description = BeautifulSoup(entity.find('field_short_description_summary').contents[0], 'html.parser').get_text()
							# short_description = str(entity.find('field_short_description_summary'))
							detect_short_description = detect(short_description)
							if detect_short_description != locale[:2]:
								detect_short_description = str(translator.detect(short_description).lang)
						except:
							detect_short_description = 'unknown'

					# write to excel row		
					output.row += [nodeID, PID, locale, detectFeatures, detectOverview, detectSpecs, detect_short_description]
					# print (nodeID + ' ' + PID +  ' ' + locale +  ' ' + features +  ' ' + overview +  ' ' + specs +  ' ' + short_description)
				else:
					continue

	# empty live product list of locale
	live_NID = []

output.save_as("contentValidation.xlsx")





		
