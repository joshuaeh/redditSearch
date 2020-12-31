#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Function to search reddit comments and submissions and
 return all metadata available and return a dataFrame """

import pandas as pd
import requests
import json
import csv
import time
import datetime

def RedditSearch(query, before='', after='', search_type='hybrid'):
    '''
    query (string)
    after (UTC Timestamp) *** Note that these must be integers ***
        DEFAULT: 7 Days before now
    before (UTC Timestamp)
        DEFAULT: now
    search_type (string)
        'comment' -> only search comments
        'submission' -> only search submissions
        'hybrid' -> search both comments and submissions
    '''
    # Defaults
    today = datetime.datetime.utcnow().timestamp()
    delta_time = datetime.timedelta(days=7)
    if not after or not before:
        after = datetime.datetime.now() - delta_time
        after = int(after.timestamp())
        before = int(today)
    print('UTC Before:', before)
    print('UTC After:', after)
    search_type = search_type.lower()
    if search_type not in ['comment', 'submission', 'hybrid']:
        print('Unknown search_type, defaulting to hybrid')
        search_type = 'hybrid'
        
    subCount = 0  # data counter
    commCount = 0  # data counter
    subStats = {} # data for storage
    commStats = {} #data storage
    subList = []
    commList = []
    
    # subfunctions
    def getPushshiftData_Submission(query, after, before):
        '''
        query(String) string to search that 
        after (Timestamp)
        before (Timestamp) 
        '''
        url = 'https://api.pushshift.io/reddit/search/submission/?q='+str(query)+\
        '&size=1000&after='+str(after)+'&before='+str(before)
        # url params well documented at https://github.com/pushshift/api for both comments and submissions
        r = requests.get(url)
        data = json.loads(r.text)
        return data['data']



    def getPushshiftData_Comments(query, after, before):
        '''
        query(String) string to search that 
        after (Timestamp)
        before (Timestamp) 
        '''
        url = 'https://api.pushshift.io/reddit/search/comment/?q='+str(query)+\
        ')&size=1000&after='+str(after)+'&before='+str(before)
        # url params well documented at https://github.com/pushshift/api for both comments and submissions
        r = requests.get(url)
        data = json.loads(r.text)
        return data['data']

        
    try:
        # Collect Submissions
        # Get initial Submissions that fit query
        if search_type != 'comment':
            print('Beginning Submission Query')
            data = getPushshiftData_Submission(query, after, before)
            # Will run until all posts have been gathered i.e. When the length of data variable = 0
            # from the 'after' date up until before date
            while len(data) > 0:
                after_ = int(data[-1]['created_utc'])
                for submission in data:
                    submission['created_utc'] = datetime.datetime.fromtimestamp(submission['created_utc'])
                    subCount+=1
                    subList.append(submission)
                # Calls getPushshiftData() with the created date of the last submission
                print('Oldest Post Date:' + str(data[-1]['created_utc']))
                #update after variable to last created date of submission
                #data has changed due to the new after variable provided by above code
                data = getPushshiftData_Submission(query, after_, before)
            print('Submission Query Finished')

        # Collect Comments
        if search_type != 'submission':
            print('Beginning Comment Query')
            data = getPushshiftData_Comments(query, after, before)
            # Will run until all posts have been gathered i.e. When the length of data variable = 0
            # from the 'after' date up until before date
            while len(data) > 0:
                after_ = int(data[-1]['created_utc'])
                for comment in data:
                    comment['created_utc'] = datetime.datetime.fromtimestamp(comment['created_utc'])
                    commCount+=1
                    commList.append(comment)
                # Calls getPushshiftData() with the created date of the last submission
                print('Oldest Comment Date:' + str((data[-1]['created_utc'])))
                #update after variable to last created date of submission
                #data has changed due to the new after variable provided by above code
                data = getPushshiftData_Comments(query, after_, before)
            print('Comment Query Finished')
    except:
        print('Error while Processing')
    
    # Convert to dfs (sub_id,created,sub,title,text,url,author,score,nsfw,numComms,permalink,flair
    print('Building Output')
    
    subDf = pd.DataFrame(subList)
    #  subDf = subDf.set_index('created_utc')
    
    commDf = pd.DataFrame(commList)
    #  commDf = commDf.set_index('created_utc')
    
    print('Number of Submissions Collected:', subCount)
    print('Number of Comments Collected:', commCount)
    return subDf, commDf


submissions, comments = RedditSearch('gummy bears')
submissions.to_csv('submissions.csv')
comments.to_csv('comments.csv')
