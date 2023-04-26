import tqdm
import asyncpraw
import re
import pandas as pd
import asyncio
from tqdm import tqdm
import pdb 
import aiohttp

CLIENT_ID='q6HKrPg90SJKqevoa6i8Tw'
CLIENT_SECRET='wlS_eetUTdF7oddrOLdABpBkQW14EQ'
USER_AGENT='nlp-toxic'
SUBREDDIT = 'news'


reddit = asyncpraw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent=USER_AGENT)
print("Connected to reddit")

#Fetching news subreddit posts
async def fetch_data(subreddit, limit):
    #pdb.set_trace()
    posts = []
    async with aiohttp.ClientSession() as session:
        news_subreddit = await reddit.subreddit(subreddit)
        top_news = news_subreddit.hot(limit=limit)
        async for post in top_news:
            posts.append([post.id])
    await session.close()
    posts = pd.DataFrame(posts,columns=['id'])
    return posts 

def preprocess(comment):
    #Removing comments that were deleted or removed by moderators 
    if comment == '[deleted]' or comment == '[removed]':
        return None
    #Converting to lower case
    comment = comment.lower()
    #Removing any urls
    comment = re.sub(r'https\S+|www.\S+','',comment)
    #Removing emojis   
    comment = comment.encode('ascii', 'ignore').decode('ascii')
    #Removing numbers
    comment = re.sub(r'\d+', '', comment)
    #Removing spaces, new lines, tabs, leading and trailing whitespaces, punctuations
    comment = comment.replace('\n','')
    comment = comment.replace('\t','')
    comment = re.sub(r'[^\w\s]', '', comment)
    #1 or more white spaces with single whitespace
    comment = re.sub(r'\s+', ' ', comment)
    #Remove leading and trailing whitespaces
    comment = comment.strip()
    if comment == '':
        return None
    return comment

#Fetching comments from the news subreddit data
async def fetch_comments_preprocess(posts):
    #pdb.set_trace()
    comments_reddit=[]
    async with aiohttp.ClientSession() as session:
        for subid in posts["id"]:
            submission = await reddit.submission(subid)
            await submission.comments.replace_more(limit=None)
            for comment in submission.comments.list():
                comment = comment.body
                if preprocess(comment) is not None:
                    comments_reddit.append(preprocess(comment))
    await session.close()
    return comments_reddit

#To save the comments in a csv file
async def save_comments(comments_reddit):
    comments_reddit = pd.DataFrame(comments_reddit,columns=['comment'])
    #Adding index to the dataframe
    comments_reddit.to_csv('../data/comments_preprocessed.csv')

#Create an asyncio event loop
loop = asyncio.get_event_loop()

#Run the async functions inside the event loop
subreddit = "news"
limit = 2
import timeit
start = timeit.default_timer()
posts = loop.run_until_complete(fetch_data(subreddit, limit))
comments = loop.run_until_complete(fetch_comments_preprocess(posts))
loop.run_until_complete(save_comments(comments))
print("Time taken: ",timeit.default_timer()-start)
#Close the event loop
loop.close()

# data = pd.read_csv('../data/comments2.csv',header=0)
# comments = data['comment'].values

# preprocessed_data = pd.DataFrame([preprocess(comment) for comment in comments if preprocess(comment) is not None],columns=['comment'])
# preprocessed_data.to_csv('../data/comments_preprocessed.csv',index=True,header=True)
