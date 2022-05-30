#%%
from functools import partial
from tkinter.tix import Select
from urllib import response
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service


#%% SpeakEV
import requests
from bs4 import BeautifulSoup,element
import pandas as pd
import urllib.parse
import time
# %%
url = 'https://www.speakev.com/search/789155/?q=fiat+500&t=post&c[child_nodes]=1&c[newer_than]=2020-01-01&c[nodes][0]=361&c[older_than]=2022-05-24&o=relevance'
page = requests.get(url)
soup = BeautifulSoup(page.content,'html.parser')

#%% find the number pages
cont = soup.find('ul',class_='pageNav-main')
page_num = cont.find_all('li')[len(cont.find_all('li'))-1].text
print(page_num)

#%%
# create the links for the pages
pages = []
temp = url.split('?q=')
for i in range(1,int(page_num)+1):    
    pages.append(temp[0] + '?page=' + str(i) + '&q=' +temp[1])
pages

# create the links for the threads
links =[]
for page in pages:
    request_page = requests.get(page)
    soup_page = BeautifulSoup(request_page.content,'html.parser')
    for link in soup_page.findAll('h3',class_='contentRow-title'):
        new_link = link.find('a').get('href')
        thread_links = urllib.parse.urljoin('https://www.speakev.com',new_link)
        links.append(thread_links)
print('Link to thread:' + str(links))
print('Sum of results:',len(links))

#%%
# create the links for each thread page (next page in each thread page)
all_links =[]
for next_link in links:    
    request_page = requests.get(next_link)
    soup_page =  BeautifulSoup(request_page.content,'html.parser')
    cont_ = soup_page.findAll('a',qid = 'page-nav-other-page')

    if len(cont_ )!= 0:
        temp = next_link.split('post-')
        for i in range(1,int(cont_[len(cont_)-1].text)+1):
            all_links.append(temp[0] + 'page-' + str(i))
    else:
        all_links.append(next_link)
print(len(all_links))

#%% Creating the function to scrape comments per thread
def scrape_comments(link):
    
    comments =[]
    usernames =[]

    page_source = requests.get(link)

    soup = BeautifulSoup(page_source.content,'html.parser')

    # get the usernamesimage.png
    usernames_tags  = soup.findAll('h4',class_='message-name california-message-user-detail')
    for username in usernames_tags:
        usernames.append(username.text)
    # print(len(usernames))


    comment_original = soup.find_all("article", {"class": "message-body js-selectToQuote"}, partial=False)

    string = "Click to expand..."

    for comment in  comment_original:
        content = comment.text
        if string in content:
            content = content.split("Click to expand...\n\n")[1]
            comments.append(content)
        else: 
            comments.append(content)


    
    result = pd.DataFrame({'Comment': comments,'Username': usernames})

    return result

#%% Scrape comments per thread on page
for link in all_links:
    df = scrape_comments(link)
    if link == links[0]:
        comments_page = df
    else:
        comments_page = pd.concat([comments_page,df], axis=0)
comments_page
# %%
comments_page.to_csv('speakEV.csv')


#%% test
# 
def scrape_user_info(link):
    
    num_user_posts = []
    usernames =[]
    profile_links =[]
    discussion_dates =[]
    joined_dates =[]

    page_source = requests.get(link)

    soup = BeautifulSoup(page_source.content,'html.parser')

    # get the usernames
    usernames_tags  = soup.findAll('h4',class_='message-name california-message-user-detail')
    for username in usernames_tags:
        usernames.append(username.text)
    # print(len(usernames))
    
    # get the link of the username profile
    for profile in usernames_tags:
        temp = profile.find('a').get('href')
        profile_link = urllib.parse.urljoin('https://www.speakev.com/',temp)
        profile_links.append(profile_link)
    # print(len(profile_links))

    # get the number of posts per user
    user_posts_tags = soup.findAll('div', qid='message-number-of-posts')
    for user_post in user_posts_tags:
        num_user_posts.append(user_post.text)
    # print(len(num_user_posts))

    # get the discussion date
    discussion_date_tags = soup.findAll('div',class_ = 'message-attribution-main')
    for discussion_date in discussion_date_tags:
        temp = discussion_date.find('time',class_='u-dt')
        discussion_dates.append(temp.text)
    # print(len(discussion_dates))

    # get the joined date of each user
    joined_dates_tags = soup.findAll('time',qid='message-register-date')
    for joined_date in joined_dates_tags:
        joined_dates.append(joined_date.text)
    # print(len(joined_dates))

    user_info = pd.DataFrame({
        'Username': usernames,
        'Link of user profile': profile_links,
        'Num of posts per user': num_user_posts,
        'Discussion Date': discussion_dates,
        'User joined date': joined_dates})

    return user_info

#%% Scrape comments per thread on page
for link in all_links:
    df = scrape_user_info(link)
    if link == links[0]:
        userinfo_data = df
    else:
        userinfo_data = pd.concat([userinfo_data,df], axis=0)
userinfo_data
# %%
userinfo_data.to_csv('userinfo_data.csv')
# %%
