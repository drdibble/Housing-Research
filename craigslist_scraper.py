zips = ['37011', '37013', '37070', '37072', '37076', '37080', '37115',
        '37116', '37138', '37189', '37201', '37202', '37203', '37204',
        '37205', '37206', '37207', '37208', '37209', '37210', '37211',
        '37212', '37213', '37214', '37215', '37216', '37217', '37218',
        '37219', '37220', '37221', '37222', '37224', '37227', '37228',
        '37229', '37230', '37232', '37234', '37235', '37236', '37238',
        '37240', '37241', '37242', '37243', '37244', '37246', '37250']

categories = ['apt', 'condo', 'cottage', 'duplex', 'flat',
            'house','in_law', 'loft', 'townhouse', 'manufactured']

from requests import get

for x in range(1,11):
    print("Working on " + categories[x-1] + "!")
    
    for zip in zips:
        print('zip code: ' + zip)
        #get the first page of the Nashville rental prices
        response = get('https://nashville.craigslist.org/search/apa?sort=date'
                       + '&search_distance=0'
                       + '&postal=' + zip 
                       + '&availabilityMode=0'
                       + '&housing_type=' + str(x)
                       + '&sale_date=all+dates')

        from bs4 import BeautifulSoup
        html_soup = BeautifulSoup(response.text, 'html.parser')

        #build out the loop
        from time import sleep
        import re
        from random import randint #avoid throttling by not sending too many requests one after the other
        from warnings import warn
        from time import time
        from IPython.core.display import clear_output
        import numpy as np

        #find the total number of posts to find the limit of the pagination
        results_num = html_soup.find('div', class_= 'search-legend')
        try: 
            results_total = int(results_num.find('span', class_='totalcount').text) #pulled the total count of posts as the upper bound of the pages array
        except AttributeError:
            continue
        #each page has 119 posts so each new page is defined as follows: s=120, s=240, s=360, and so on. So we need to step in size 120 in the np.arange function
        pages = np.arange(0, results_total+1, 120)

        iterations = 0

        post_timing = []
        post_hoods = []
        post_title_texts = []
        bedroom_counts = []
        sqfts = []
        post_links = []
        post_prices = []
        post_zip = []

        for page in pages:
            
            #get request
            response = get("https://nashville.craigslist.org/search/apa?" 
                           + "s=" #the parameter for defining the page number 
                           + str(page) #the page number in the pages array from earlier
                           + "&search_distance=0"
                           + "&postal=" + zip
                           + "&availabilityMode=0"
                           + "&housing_type=" + str(x)
                           + "&sale_date=all+dates")

            sleep(randint(1,5))
             
            #throw warning for status codes that are not 200
            if response.status_code != 200:
                warn('Request: {}; Status code: {}'.format(requests, response.status_code))
                
            #define the html text
            page_html = BeautifulSoup(response.text, 'html.parser')
            
            #define the posts
            posts = html_soup.find_all('li', class_= 'result-row')
                
            #extract data item-wise
            for post in posts:
                
                post_zip = zip

                if post.find('span', class_ = 'result-hood') is not None:

                    #posting date
                    #grab the datetime element 0 for date and 1 for time
                    post_datetime = post.find('time', class_= 'result-date')['datetime']
                    post_timing.append(post_datetime)

                    #neighborhoods
                    post_hood = post.find('span', class_= 'result-hood').text
                    post_hoods.append(post_hood)

                    #title text
                    post_title = post.find('a', class_='result-title hdrlnk')
                    post_title_text = post_title.text
                    post_title_texts.append(post_title_text)

                    #post link
                    post_link = post_title['href']
                    post_links.append(post_link)
                    
                    #removes the \n whitespace from each side, removes the currency symbol, and turns it into an int 
                    post_price = post.a.text.strip()
                    post_price = post_price.replace('$', '')
                    if post_price == '':
                        post_price = np.nan
                    post_price = float(post_price)
                    #print(post_price)
                    post_prices.append(post_price)
                    
                    if post.find('span', class_ = 'housing') is not None:
                        
                        #if the first element is accidentally square footage
                        if 'ft2' in post.find('span', class_ = 'housing').text.split()[0]:
                            
                            #make bedroom nan
                            bedroom_count = np.nan
                            bedroom_counts.append(bedroom_count)
                            
                            #make sqft the first element
                            sqft = int(post.find('span', class_ = 'housing').text.split()[0][:-3])
                            sqfts.append(sqft)
                            
                        #if the length of the housing details element is more than 2
                        elif len(post.find('span', class_ = 'housing').text.split()) > 2:
                            
                            #therefore element 0 will be bedroom count
                            bedroom_count = post.find('span', class_ = 'housing').text.replace("br", "").split()[0]
                            bedroom_counts.append(bedroom_count)
                            
                            #and sqft will be number 3, so set these here and append
                            sqft = int(post.find('span', class_ = 'housing').text.split()[2][:-3])
                            sqfts.append(sqft)
                            
                        #if there is num bedrooms but no sqft
                        elif len(post.find('span', class_ = 'housing').text.split()) == 2:
                            
                            #therefore element 0 will be bedroom count
                            bedroom_count = post.find('span', class_ = 'housing').text.replace("br", "").split()[0]
                            bedroom_counts.append(bedroom_count)
                            
                            #and sqft will be number 3, so set these here and append
                            sqft = np.nan
                            sqfts.append(sqft)                    
                        
                        else:
                            bedroom_count = np.nan
                            bedroom_counts.append(bedroom_count)
                        
                            sqft = np.nan
                            sqfts.append(sqft)
                        
                    #if none of those conditions catch, make bedroom nan, this won't be needed    
                    else:
                        bedroom_count = np.nan
                        bedroom_counts.append(bedroom_count)
                        
                        sqft = np.nan
                        sqfts.append(sqft)
                    #    bedroom_counts.append(bedroom_count)
                        
                    #    sqft = np.nan
                    #    sqfts.append(sqft)
                        
            iterations += 1
            print("Page " + str(iterations) + " scraped successfully!")

        print("\n")

        print("Scrape complete!")

        import pandas as pd

        nash_apts = pd.DataFrame({'posted': post_timing,
                               'neighborhood': post_hoods,
                               'post title': post_title_texts,
                               'number bedrooms': bedroom_counts,
                                'sqft': sqfts,
                                'URL': post_links,
                               'price': post_prices,
                                'zip': post_zip})
        #print(nash_apts.info())
        #nash_apts.head(10)


        #first things first, drop duplicate URLs because people are spammy on Craigslist. 
        #Let's see how many uniqe posts we really have.
        nash_apts = nash_apts.drop_duplicates(subset='URL')
        len(nash_apts.drop_duplicates(subset='URL'))

        #make the number bedrooms to a float (since np.nan is a float too)
        nash_apts['number bedrooms'] = nash_apts['number bedrooms'].apply(lambda x: float(x))

        #convert datetime string into datetime object to be able to work with it
        from datetime import datetime

        nash_apts['posted'] = pd.to_datetime(nash_apts['posted'])

        #Looking at what neighborhoods there are with eb_apts['neighborhood'].unique() allowed me to see what
        #I needed to deal with in terms of cleaning those.

        #remove the parenthesis from the left and right of the neighborhoods
        nash_apts['neighborhood'] = nash_apts['neighborhood'].map(lambda x: x.lstrip(' (').rstrip(')'))

        #titlecase them
        nash_apts['neighborhood'] = nash_apts['neighborhood'].str.title()

        #just take the first name of the neighborhood list, splitting on the '/' delimiter
        nash_apts['neighborhood'] = nash_apts['neighborhood'].apply(lambda x: x.split('/')[0])

        #fix one-offs that
        nash_apts['neighborhood'].replace('Near The Mall At Green Hills', 'Green Hills', inplace=True)
        nash_apts['neighborhood'].replace('DOWNTOWN', 'Downtown', inplace=True)
        nash_apts['neighborhood'].replace('Downtown Nashville', 'Downtown', inplace=True)
        nash_apts['neighborhood'].replace('GERMANTOWN', 'Germantown', inplace=True)
        nash_apts['neighborhood'].replace('Nashville-Germantown-152', 'Germantown', inplace=True)
        nash_apts['neighborhood'].replace('The Monroe Germantown #152', 'Germantown', inplace=True)
        nash_apts['neighborhood'].replace('MIDTOWN', 'Midtown', inplace=True)
        nash_apts['neighborhood'].replace('midtown', 'Midtown', inplace=True)
        nash_apts['neighborhood'].replace('Aertson Midtown #1103', 'Midtown', inplace=True)
        nash_apts['neighborhood'].replace('Nashville-Midtown-1103', 'Midtown', inplace=True)
        nash_apts['neighborhood'].replace('MUSIC ROW', 'Music Row', inplace=True)
        nash_apts['neighborhood'].replace('GULCH', 'Gulch', inplace=True)
        nash_apts['neighborhood'].replace('Gulch Nashville', 'Gulch', inplace=True)
        nash_apts['neighborhood'].replace('Nashville_Tn', 'Nashville', inplace=True)
        nash_apts['neighborhood'].replace('Nashville, Tn', 'Green Hills', inplace=True)
        nash_apts['neighborhood'].replace('Nashville**', 'Nashville', inplace=True)
        nash_apts['neighborhood'].replace('Nashville-Tn', 'Nashville', inplace=True)
        nash_apts['neighborhood'].replace('West-End', 'West End', inplace=True)

        #remove whitespaces
        nash_apts['neighborhood'] = nash_apts['neighborhood'].apply(lambda x: x.strip())

        #save the clean data
        nash_apts.to_csv(zip + "_" + categories[x-1] + ".csv", index=False)

