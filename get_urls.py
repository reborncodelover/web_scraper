import csv
import requests
from bs4 import BeautifulSoup

all_charities = []
# Scrape from the archive snapshot rather than live Charity Navigator site
starting_url = "https://web.archive.org/web/20160705164956/http://www.charitynavigator.org/index.cfm?bay=search.alpha&ltr=1"

top_page = requests.get(starting_url)
top_soup = BeautifulSoup(top_page.text, 'html.parser')

# loop through every alphabet letter shown in the top nav link
for letter in top_soup.find(id='maincontent2').find('p').find_all('a'): 
	base_url = starting_url[:-1]
	starting_url = base_url + letter.text
	print ("Getting urls of charities starting with the letter: '" , letter.text, "'")

	page = requests.get(starting_url)
	soup = BeautifulSoup(page.text, 'html.parser')

	# section on the page with the list of charities that start with current letter
	charities_section = soup.find(id= 'maincontent2') 

	# drop both top and bottom nav links
	top_nav_links = charities_section.find('p')
	top_nav_links.decompose() # drop the top nav links
	bottom_nav_links = charities_section.find('p')
	bottom_nav_links.decompose() # drop the bottom nav links too

	# Now loop through and find all the charities listed in the page
	charities_list = charities_section.find_all('a')
	for charity in charities_list:
		item = charity.get('href')
		charity_url = item
		charity_id = item[item.find('orgid=')+len('orgid='):]
		charity_name = charity.contents[0] 
		# Hint: alternately you could use charity.text to get charity name

		all_charities.append([charity_id, charity_name, charity_url])
		#print (charity_id, " : ", charity_name)

print("Total number of charities:", len(all_charities))
#print (all_charities)

with open('all_charities_urls.csv', 'w') as csvfile:
	fwriter = csv.writer(csvfile)
	[fwriter.writerow(row) for row in all_charities]
