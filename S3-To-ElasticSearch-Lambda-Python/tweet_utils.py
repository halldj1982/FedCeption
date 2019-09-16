#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Oct 20, 2015

@author: mentzera
'''
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

#https://www.elastic.co/blog/strings-are-dead-long-live-strings
tweet_mapping_v5 = 	{'properties': {
							'timestamp_ms': { 
								'type': 'date'
							},
							'text': {
								'type': 'text'
							},
							'sentiments': {
								'type': 'keyword'
							},
							'sentiment_assessment_tokens': {
								'type': 'keyword'
							},
							'sentiment_assessment_polarities': {
								'type': 'double'
							},
							'sentiment_assessment_subjectivities': {
								'type': 'double'
							}
						}
					}

def _sentiment_analysis(tweet):
	tweet['emoticons'] = []
	tweet['sentiments'] = []
	_sentiment_analysis_by_emoticons(tweet)
	if len(tweet['sentiments']) == 0:
		_sentiment_analysis_by_text(tweet)


def _sentiment_analysis_by_emoticons(tweet):
	for sentiment, emoticons_icons in emoticons.iteritems():
		matched_emoticons = re.findall(emoticons_icons, tweet['text'].encode('utf-8'))
		if len(matched_emoticons) > 0:
			tweet['emoticons'].extend(matched_emoticons)
			tweet['sentiments'].append(sentiment)

	if Sentiments.POSITIVE in tweet['sentiments'] and Sentiments.NEGATIVE in tweet['sentiments']:
		tweet['sentiments'] = Sentiments.CONFUSED
	elif Sentiments.POSITIVE in tweet['sentiments']:
		tweet['sentiments'] = Sentiments.POSITIVE
	elif Sentiments.NEGATIVE in tweet['sentiments']:
		tweet['sentiments'] = Sentiments.NEGATIVE

def _sentiment_analysis_by_text(tweet):
	blob = TextBlob(tweet['text'].decode('ascii', errors="replace"))
	sentiment_polarity = blob.sentiment.polarity
	if sentiment_polarity < 0:
		sentiment = Sentiments.NEGATIVE
	elif sentiment_polarity <= 0.2:
		sentiment = Sentiments.NEUTRAL
	else:
		sentiment = Sentiments.POSITIVE
	tweet['sentiments'] = sentiment
	
	sentiment_tokens = [];
	sentiment_polarities = [];
	sentiment_subjectivities = [];

	for sentiment_assessment in blob.sentiment_assessments.assessments:
		sentiment_tokens.append(sentiment_assessment[0][0])
		sentiment_polarities.append(sentiment_assessment[1])
		sentiment_subjectivities.append(sentiment_assessment[2])

	tweet['sentiment_assessment_tokens'] = sentiment_tokens
	tweet['sentiment_assessment_polarities'] = sentiment_polarities
	tweet['sentiment_assessment_subjectivities'] = sentiment_subjectivities

def get_tweet(doc):
	tweet = {}
	tweet[id_field] = doc[id_field]
	tweet['hashtags'] = map(lambda x: x['text'],doc['hashtags'])
	tweet['timestamp_ms'] = dateutil.parser.parse(doc['created_at']);
	tweet['text'] = doc['text']
	tweet['mentions'] = re.findall(r'@\w*', doc['text'])
	_sentiment_analysis(tweet)
	return tweet

def get_tweet_mapping(es_version_number_str):
	return tweet_mapping_v5