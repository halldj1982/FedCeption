#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from textblob import TextBlob
from datetime import datetime
import dateutil.parser

class Sentiments:
    POSITIVE = 'Positive'
    NEGATIVE = 'Negative'
    NEUTRAL = 'Neutral'
    CONFUSED = 'Confused'
    
id_field = 'id_str'
emoticons = {Sentiments.POSITIVE:'😀|😁|😂|😃|😄|😅|😆|😇|😈|😉|😊|😋|😌|😍|😎|😏|😗|😘|😙|😚|😛|😜|😝|😸|😹|😺|😻|😼|😽',
             Sentiments.NEGATIVE : '😒|😓|😔|😖|😞|😟|😠|😡|😢|😣|😤|😥|😦|😧|😨|😩|😪|😫|😬|😭|😾|😿|😰|😱|🙀',
             Sentiments.NEUTRAL : '😐|😑|😳|😮|😯|😶|😴|😵|😲',
             Sentiments.CONFUSED: '😕'
             }



def _sentiment_analysis(tweet_data):
	tweet_data['emoticons'] = []
	tweet_data['sentiments'] = []
	_sentiment_analysis_by_emoticons(tweet_data)
	if len(tweet_data['sentiments']) == 0:
		_sentiment_analysis_by_text(tweet_data)


def _sentiment_analysis_by_emoticons(tweet_data):
	for sentiment, emoticons_icons in emoticons.iteritems():
		matched_emoticons = re.findall(emoticons_icons, tweet_data['status']['text'].encode('utf-8'))
		if len(matched_emoticons) > 0:
			tweet_data['emoticons'].extend(matched_emoticons)
			tweet_data['sentiments'].append(sentiment)

	if Sentiments.POSITIVE in tweet_data['sentiments'] and Sentiments.NEGATIVE in tweet_data['sentiments']:
		tweet_data['sentiments'] = Sentiments.CONFUSED
	elif Sentiments.POSITIVE in tweet_data['sentiments']:
		tweet_data['sentiments'] = Sentiments.POSITIVE
	elif Sentiments.NEGATIVE in tweet_data['sentiments']:
		tweet_data['sentiments'] = Sentiments.NEGATIVE

def _sentiment_analysis_by_text(tweet_data):
	blob = TextBlob(tweet_data['status']['text'].decode('ascii', errors="replace"))
	sentiment_polarity = blob.sentiment.polarity
	if sentiment_polarity < 0:
		sentiment = Sentiments.NEGATIVE
	elif sentiment_polarity <= 0.2:
		sentiment = Sentiments.NEUTRAL
	else:
		sentiment = Sentiments.POSITIVE
	tweet_data['sentiments'] = sentiment
	
	sentiment_tokens = [];
	sentiment_polarities = [];
	sentiment_subjectivities = [];

	for sentiment_assessment in blob.sentiment_assessments.assessments:
		sentiment_tokens.append(sentiment_assessment[0][0])
		sentiment_polarities.append(sentiment_assessment[1])
		sentiment_subjectivities.append(sentiment_assessment[2])

	tweet_data['sentiment_assessment_tokens'] = sentiment_tokens
	tweet_data['sentiment_assessment_polarities'] = sentiment_polarities
	tweet_data['sentiment_assessment_subjectivities'] = sentiment_subjectivities

def get_tweet(doc):
	tweet = {}
	tweet_data = {}

	tweet['search_metadata'] = doc['search_metadata']
	tweet_data['status'] = doc['status']
	_sentiment_analysis(tweet_data)
	tweet['tweet_data'] = tweet_data
	return tweet

def get_tweet_mapping(es_version_number_str):
	return tweet_mapping_v5