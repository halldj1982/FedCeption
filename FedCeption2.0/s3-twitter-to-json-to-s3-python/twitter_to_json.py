
import config
from tweet_utils import get_tweet, id_field, get_tweet_mapping

def load(tweets):       
    counter = 0
    bulk_data = []
    list_size = len(tweets)
    for doc in tweets:
        tweet = get_tweet(doc)
        bulk_data.append(tweet)
        counter+=1
    return bulk_data
