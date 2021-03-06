# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
import pymongo

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": mars_hemispheres(browser),
        "last_modified": dt.datetime.now()
    }
    browser.quit()
    #print(data["facts"])
    return data


# Set the executable path and initialize the chrome browser in splinter
#executable_path = {'executable_path': 'chromedriver'}
#browser = Browser('chrome', **executable_path)

# Visit the mars nasa news site
def mars_news(browser):
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_summery = slide_elem.find("div", class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None


    return news_title, news_summery
    

def featured_image(browser):
    # The following cells are to gather images from Nasa's Space Images
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()
    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()
    
    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    
    except AttributeError:
        return None
    
    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    
    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a datafram
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def  mars_hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    
    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []
    beg_url = "https://astrogeology.usgs.gov"
    
    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    soups_1 = soup(html, 'html.parser')
    articles = soups_1.find_all('div', class_='item')
    
    for article in articles:
        h3= article.find('h3').text
        link = article.find('a')
        href = link['href']
        pg_url = (beg_url + href)
        
        browser.visit(pg_url)
        html = browser.html
        soups = soup(html, 'html.parser')
        imgs = soups.find_all('img', class_="wide-image")
        for img in imgs:
            img_end_url = img["src"]
            
            full_img_url = (beg_url + img_end_url)
        
            hemispheres = {'img_url': full_img_url, 'title' : h3}
        
            hemisphere_image_urls.append(hemispheres)

    return hemisphere_image_urls


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())