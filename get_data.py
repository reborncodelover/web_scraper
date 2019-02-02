import csv
import requests
from bs4 import BeautifulSoup

'''
First read the CSV data produced by get_urls.py program. 
Each entry in the CSV file has 3 elements. Unique charity_id given by Charity Navigator, 
charity_name and the URL where all the details on that charity can be seen and scarped.
'''
all_charities = []
all_charities_data = []
data_missing_charities = []
with open('all_charities_urls.csv') as csvfile:
	freader = csv.reader(csvfile)
	for row in freader:
		all_charities.append(row)

# See how many charities are there
#print("Number of charities:", len(all_charities))
# Print the data retrived from the file.
#[print('{:10s} | {:s}'.format(charity[0],  charity[1])) for charity in all_charities]

#test_count = 200

# Now actually scrape all the key details pertaining to the charities one charity at a time
for charity in all_charities:

# This bit of code allows us to test our code first with a smaller number of charities
	'''
	if (test_count == 0):
		break
	else:
		test_count -= 1
	'''
	
	charity_id = charity[0]
	charity_name = charity[1] 
	url = charity[2] # the url where we need to scrape the required data
	page = requests.get(url) # get the actual web page that has required details
	soup = BeautifulSoup(page.text, 'html.parser') # parse the web page 

	charity_street_addr = [] # to store multiline postal address
	charity_tel = charity_fax = charity_ein = charity_website = None
	charity_core_service = charity_tagline = None
	charity_overall_rating = charity_financial_rating = charity_transparency_rating = None
	charity_program_expenses = charity_administrative_expenses = None
	charity_fundraising_expenses = charity_fundraising_efficiency = None
	charity_primary_revenue_growth = charity_expenses_growth = charity_working_capital_ratio = None

	# First look at the left nav that has contact details of the charity
	try:
		whole_left_nav = soup.find(id='leftnavcontent').find(class_='rating').find_all('p')
		left_nav_para1 = whole_left_nav[0] # first para has name, postal address and phone / fax numbers
		left_nav_para1.find('a').decompose() # get rid of the unnecessary link in that para
		address_section = left_nav_para1.text # just get the text alone and drop all the html markup
		address_lines = address_section.splitlines() # split the multiline address section
		# charity_name = address_lines[0] # charity name is the first line

		for address_line in address_lines[1:]: # skipping first line as we know it is charity name
			stripped = address_line.strip(' \t\n').replace(u'\xa0',' ') # strip unncessary charachters
			if len(stripped) == 0:
				pass # skipping as this address line has only unnecessary characters
			else:
				if stripped.startswith(": "): # the Employer ID Number EIN line has leading ": "
					charity_ein = stripped[2:] # just get the EIN
				elif stripped.startswith("tel: "): # for many phone and fax numbers are in the same line
					tel_and_or_fax = stripped[5:]
					charity_tel = tel_and_or_fax[:14]
					tel_and_or_fax = tel_and_or_fax[14:]
					if ("Fax: " in tel_and_or_fax or "fax: " in tel_and_or_fax):
						charity_fax = tel_and_or_fax[6:]
				elif stripped.startswith("fax: ") or stripped.startswith("Fax: "):
					charity_fax = stripped[5:]
				else:
					charity_street_addr.append(stripped)
			

		# Now look at the remaining paras for actual website address 
		for left_nav_para in whole_left_nav[1:]: # skip the first para tag as it doesn't have the website url for charity
			all_anchors = left_nav_para.find_all('a')
			for anchor in all_anchors:
				if (anchor.text == "Visit Web Site"):
					website = anchor.get('href')
					# rindex() gives the last instance of substring in the string being searched
					# use that to identify the start of actual website url
					charity_website = website[website.rindex("http"):] 
		
		#print('Name: ', charity_name)
		#print('Website: ', charity_website)
		#print('Street Address: ', charity_street_addr)
		#print('EIN: ', charity_ein)
		#print('Tel: ', charity_tel)
		#print('Fax: ', charity_fax)

	except:
		print('Skipping charity due to missing Contact Data: ', charity_id, charity_name)
		data_missing_charities.append(["Contact Data", charity_id, charity_name, url]);
		continue


	# Now lets get some valuable performance data given by Charity Navigator
	try:
		rating_sections = soup.find(id='maincontent2').find(class_='rating').find_all(class_='shadedtable')
		#print("Performance data Found for ", charity_name)
		charity_core_service = soup.find(id='maincontent2').find(class_='crumbs').text
		charity_tagline = soup.find(id='maincontent2').find(class_='tagline').text
	
		#for idx, section in enumerate(rating_sections):
			#print ('Index: ', idx, section.text)
	
		#rating_section = rating_sections[0] # first section gives top level performance metrics
	
		for rating_section in rating_sections:
			if "Overall" in rating_section.text and \
				"Financial" in rating_section.text and \
				"Accountability & Transparency" in rating_section.text:
				rating_data = rating_section.find_all('td')
				charity_overall_rating = rating_data[1].text
				charity_financial_rating = rating_data[4].text
				charity_transparency_rating = rating_data[7].text
	
			elif "Program Expenses" in rating_section.text:
				rating_data = rating_section.find_all('td')
				charity_program_expenses = rating_data[2].text
				charity_administrative_expenses = rating_data[5].text
				charity_fundraising_expenses = rating_data[8].text
				charity_fundraising_efficiency = rating_data[11].text
				charity_primary_revenue_growth = rating_data[14].text
				charity_expenses_growth = rating_data[17].text
				charity_working_capital_ratio = rating_data[20].text
	
		#print('Services: ', charity_core_service)
		#print('Tagline: ', charity_tagline)
		#print('Overall Rating: ', charity_overall_rating)
		#print('Financial  Rating: ', charity_financial_rating)
		#print('Transparency  Rating: ', charity_transparency_rating)
		#print('Program Expenses: ', charity_program_expenses)
		#print('Adminstrative Expenses: ', charity_administrative_expenses)
		#print('Fundaraising Expenses: ', charity_fundraising_expenses)
		#print('Fundraising Efficiency: ', charity_fundraising_efficiency)
		#print('Primary Revenue Growth: ', charity_primary_revenue_growth)
		#print('Program Expenses Growth: ', charity_expenses_growth)
		#print('Working Capital Ratio (years): ', charity_working_capital_ratio)
		#print()
	except:
		print('Skipping charity due to missing Performance Data: ', charity_id, charity_name)
		data_missing_charities.append(["Performance Data", charity_id, charity_name, url]);
		continue

	print("Successfully scraped data for: ", charity_id, charity_name)
	all_charities_data.append([charity_id, charity_name, charity_ein, charity_street_addr, \
		charity_tel, charity_fax, \
		charity_overall_rating, charity_financial_rating, charity_transparency_rating, \
		charity_program_expenses, charity_administrative_expenses, charity_fundraising_expenses, \
		charity_fundraising_efficiency, charity_primary_revenue_growth, charity_expenses_growth, \
		charity_working_capital_ratio, charity_core_service, charity_tagline, charity_website, url])



with open('all_charities_data.csv', 'w') as csvfile:
	fwriter = csv.writer(csvfile)
	# write the header row first
	fwriter.writerow(['Charity_ID', 'Charity_Name', 'EIN', 'Street_Address', \
		'Telephone', 'Fax', \
		'Overall_Rating', 'Financial_Rating', 'Transparency_Rating', \
		'Program_Expenses', 'Administrative_Expenses', 'Fundraising_Expenses', \
		'Fundraising_Efficiency', 'Revenue_Growth', 'Expenses_Growth', \
		'Working_Capital_Ratio', 'Core_Service', 'Tagline', 'Website', 'Scraped_From'])
	# write all data rows after that
	[fwriter.writerow(row) for row in all_charities_data]

with open('data_missing_charities.csv', 'w') as csvfile:
	fwriter = csv.writer(csvfile)
	[fwriter.writerow(row) for row in data_missing_charities]
