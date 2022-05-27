import pandas as pd 
import numpy as np
from tqdm.notebook import tqdm
tqdm.pandas()

from fuzzywuzzy import fuzz


class DE_class:
	def __init__(self, link):
		self.df = pd.read_csv(link)
		self.link = link
		self.symbols = "!@#$%^&*() -"
		self.phone_variable_list = ['Phone','Match_Phone'
		,'Match_Phone_2__c','Match_Phone_3__c'
		,'Match_Phone_4__c','Match_Phone_5__c']
		self.email_variable_list = ['Email',
									 'Match_Email',
									 'Match_Email_2__c',
									 'Match_Email_3__c',
									 'Match_Verified_Email__c']
		self.web_variable_list = ['Web', 'Match_Web_Site_1__c', 'Match_Web_Site_2__c', 'Match_Web_Site_3__c']
		self.fax_variable_list = ['fax', 'Match_Fax', 'Match_Fax_2__c', 'Match_Fax_3__c']
		self.state_variable_list = ['state',
									 'Match_Bar_Admission_State_1__c',
									 'Match_Bar_Admission_State_2__c',
									 'Match_Bar_Admission_State_3__c',
									 'Match_Bar_Admission_State_4__c',
									 'Match_Bar_Admission_State_5__c']
		self.zip_variable_list = ['zip', 'Match_Zip_Code_1__c', 'Match_Zip_Code_2__c', 'Match_Zip_Code_3__c'] 		
		self.street_variable_list = ['street',
									 'Match_MailingStreet',
									 'Match_OtherStreet',
									 'Match_Street_Address_1__c',
									 'Match_Street_Address_2__c',
									 'Match_Street_Address_3__c']				
		self.city_variable_list = ['city',
									 'Match_City_1__c',
									 'Match_City_2__c',
									 'Match_City_3__c']		
		self.firm_name_variable_list = []
		self.pratice_area_variable_list = []


		self.column_fixer()

		#preprocessing
		self.clean_phone()
		self.clean_fax()
		self.clean_zip()
		self.phone_comparator()
		self.fax_comparator()
		self.email_comaparator()
		self.web_comaparator()
		self.state_comaparator()
		self.zip_comparator()
		self.list_comparator_fuzzy([self.street_variable_list, self.city_variable_list])
		self.get_vacant_field(Phone = self.phone_variable_list, Fax = self.fax_variable_list, Email = self.email_variable_list,
								Web = self.web_variable_list, State = self.state_variable_list, zip = self.zip_variable_list, Street = self.street_variable_list,
								City = self.city_variable_list)
		# self.get_output()

	def clean_phone(self):
		for phone in self.phone_variable_list:
			self.df[phone + ' - cleaned'] = self.df.apply(lambda x: self.symbol_remover(x[phone]), axis = 1)

	def clean_fax(self):
		for fax in self.fax_variable_list:
			self.df[fax + ' - cleaned'] = self.df.apply(lambda x: self.symbol_remover(x[fax]), axis = 1)		

	def clean_zip(self):
		for zip in self.zip_variable_list:
			self.df[zip + ' - cleaned'] = self.df.apply(lambda x: self.symbol_remover(x[zip]), axis = 1)				

	def symbol_remover(self, value):
		value = str(value)
		for symbol in self.symbols:
			value = value.replace(symbol, "")
		return value

	def fuzzymatch(self, value1, value2):
		return fuzz.token_sort_ratio(value1, value2)

	def comparator(self, value, list):
		if str(value) != 'nan':
			if value in list:
				return True
			else:
				return False
		else:
			return "No value"

	def comparator_fuzzy(self, value, list):
		temp_list = []

		if str(value) != 'nan':
			for sf_value in list:
				temp_list.append(self.fuzzymatch(value, sf_value))
			if max(temp_list) >= 75:
				return True
			else:
				return False
		else:
			return "No value"

	def phone_comparator(self):
		value = self.phone_variable_list[0] + ' - cleaned'
		list = [x + ' - cleaned' for x in self.phone_variable_list[1:]]

		self.df[value + ' Found in SF'] = self.df.apply(lambda x: self.comparator(x[value], [x[y] for y in list]), axis = 1)

	def fax_comparator(self):
		value = self.fax_variable_list[0] + ' - cleaned'
		list = [x + ' - cleaned' for x in self.fax_variable_list[1:]]

		self.df[value + ' Found in SF'] = self.df.apply(lambda x: self.comparator(x[value], [x[y] for y in list]), axis = 1)	

	def zip_comparator(self):
		value = self.zip_variable_list[0] + ' - cleaned'
		list = [x + ' - cleaned' for x in self.zip_variable_list[1:]]

		self.df[value + ' Found in SF'] = self.df.apply(lambda x: self.comparator(x[value], [x[y] for y in list]), axis = 1)	


	def email_comaparator(self):
		value = self.email_variable_list[0]
		list = self.email_variable_list[1:]

		self.df[value + ' Found in SF'] = self.df.apply(lambda x: self.comparator_fuzzy(x[value], [x[y] for y in list]), axis = 1)


	def web_comaparator(self):

		# for review, there are values with www. and the salesforce value does not have

		value = self.web_variable_list[0]
		list = self.web_variable_list[1:]

		self.df[value + ' Found in SF'] = self.df.apply(lambda x: self.comparator_fuzzy(x[value], [x[y] for y in list]), axis = 1)


	def state_comaparator(self):

		value = self.state_variable_list[0]
		list = self.state_variable_list[1:]

		self.df[value + ' Found in SF'] = self.df.apply(lambda x: self.comparator_fuzzy(x[value], [x[y] for y in list]), axis = 1)

	def list_comparator_fuzzy(self, searches):


		for search in searches:
			value = search[0]
			list = search[1:]

			self.df[value + ' Found in SF'] = self.df.apply(lambda x: self.comparator_fuzzy(x[value], [x[y] for y in list]), axis = 1)

	def column_fixer(self):
		self.all_variable_list = self.phone_variable_list + self.email_variable_list + self.web_variable_list + self.fax_variable_list + self.state_variable_list + self.zip_variable_list + self.street_variable_list + self.city_variable_list
		self.lacking_variable_list = list(set(self.all_variable_list) - set(self.df.columns.tolist()))

		for x in self.lacking_variable_list:
			self.df[x] = np.nan

	def get_vacant_field(self, **kwargs):
		def checker(value_list, column_list):
			for value in enumerate(value_list):
				if str(value[1]) == 'nan':
					return column_list[value[0]]
		for key,list in kwargs.items():
			print(list)
			temp_list = list[1:]
			self.df[key + ' - Vacant Field'] = self.df.apply(lambda x: checker([x[i] for i in temp_list], temp_list), axis = 1)

	def get_output(self,key_guide):
		if 'Match_AccountId' in self.df.columns.tolist():
			self.web_scraped_columns = ['Match_AccountId', 'Match_Id','First and Last', 'First Name', 'Last Name', 'suffix', 'status',
		'Phone', 'phoneExt', 'fax', 'Web', 'street', 'city', 'state', 'zip',
		'Email', 'Bar Admission Date', 'Bar State']
		else:
			self.web_scraped_columns = ['Match_Id','First and Last', 'First Name', 'Last Name', 'suffix', 'status',
		'Phone', 'phoneExt', 'fax', 'Web', 'street', 'city', 'state', 'zip',
		'Email', 'Bar Admission Date', 'Bar State']

		self.found_in_sf_columns = [x for x in self.df.columns if 'found in sf' in x.lower()]

		self.vacant_field_columns = [x for x in self.df.columns if 'vacant field' in x.lower()]

		self.needed_columns = []
		self.needed_columns.extend(self.web_scraped_columns)
		self.needed_columns.extend(self.found_in_sf_columns)
		self.needed_columns.extend(self.vacant_field_columns)

		print(self.needed_columns)

		self.output = self.df[self.needed_columns].copy()

		temp_list = []
		for index, column in enumerate(self.vacant_field_columns):
			# self.get_value(column)
			print(f"index: {index} | ", f"column: {column} | ", f"found in sf: {self.found_in_sf_columns[index]}")
			temp_list.append(self.output.pivot(columns = column, values = key_guide[column]))

		self.final_output = pd.concat(temp_list, axis = 1)

		self.output = self.output.merge(self.final_output, right_index=True, left_index=True)





