/***
Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Amazon Software License (the "License").
You may not use this file except in compliance with the License.
A copy of the License is located at

http://aws.amazon.com/asl/

or in the "license" file accompanying this file. This file is distributed
on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
express or implied. See the License for the specific language governing
permissions and limitations under the License.
***/

//'use strict';

var config = require('C:/temp/config');
var Twitter = require('twitter');
var util = require('util');
var logger = require('./util/logger');

function twitterStreamProducer(firehose) {
  var log = logger().getLogger('producer');
  var waitBetweenPutRecordsCallsInMilliseconds = config.waitBetweenPutRecordsCallsInMilliseconds;
  var T = new Twitter(config.twitter)

  // Creates a new kinesis stream if one doesn't exist.
  function _createStreamIfNotCreated(callback) {
    firehose.describeDeliveryStream({DeliveryStreamName: config.firehose.DeliveryStreamName}, function(err, data) {
      if (err) {
        firehose.createDeliveryStream(config.firehose, function(err, data) {
          if (err) {
            // ResourceInUseException is returned when the stream is already created.
            if (err.code !== 'ResourceInUseException') {
              console.log(err);
              callback(err);
              return;
            }
            else {
              var msg = util.format('%s stream is already created! Re-using it.', config.firehose.DeliveryStreamName);
              console.log(msg);
              log.info(msg);
            }
          }
          else {
            var msg = util.format('%s stream does not exist. Created a new stream with that name.', config.firehose.DeliveryStreamName);
            console.log(msg);
            log.info(msg);
          }
          // Poll to make sure stream is in ACTIVE state before start pushing data.
          _waitForStreamToBecomeActive(callback);
        });
      }
      else {
        var msg = util.format('%s stream is already created! Re-using it.', config.firehose.DeliveryStreamName);
        log.info(msg);
      }

      // Poll to make sure stream is in ACTIVE state before start pushing data.
      _waitForStreamToBecomeActive(callback);
    });

    
  }

  // Checks current status of the stream.
  function _waitForStreamToBecomeActive(callback) {
    firehose.describeDeliveryStream({DeliveryStreamName: config.firehose.DeliveryStreamName}, function(err, data) {
      if (!err) {
        if (data.DeliveryStreamDescription.DeliveryStreamStatus === 'ACTIVE') {
          log.info('Current status of the stream is ACTIVE.');
          callback(null);
        }
        else {
          var msg = util.format('Current status of the stream is %s.', data.DeliveryStreamDescription.DeliveryStreamStatus);
          console.log(msg);
          log.info(msg);
          setTimeout(function() {
            _waitForStreamToBecomeActive(callback);
          }, 1000 * config.waitBetweenDescribeCallsInSeconds);
        }
      }
    });
  }


  function _sendToFirehose() {


    var params = {
      q: 'Federal Reserve',
      count: 100
    }

    var records = [];
    var record = {};
    var recordParams = {};

    T.get('search/tweets', params, function (err, data) {
      if (err) {
        console.log("Error = " + JSON.stringify(err));
      }
     
      var tweets = data.statuses;
      
      for (const tweet of tweets) {
        log.info("Tweet Created at = " + tweet.created_at);
        log.info("Tweet Text = " + tweet.text);
        log.info("Tweet Hashtags = " + tweet.entities.hashtags);
        log.info("Tweet Id = " + tweet.id_str);
        var tweetDataToUpload = {id_str: tweet.id_str, created_at:tweet.created_at, text:tweet.text, hashtags:tweet.entities.hashtags}
        recordParams = {
            DeliveryStreamName: config.firehose.DeliveryStreamName,
            Record: {
              Data: JSON.stringify(tweetDataToUpload)+',\n'
            }
        }; 

        firehose.putRecord(recordParams, function(err, data) {

          log.info("Firehose put response = " + JSON.stringify(data));
          if (err) {
            log.error(err);
          }
        });
      }  

     
    });
  }


  return {
    run: function() {
      log.info(util.format('Configured wait between consecutive PutRecords call in milliseconds: %d',
          waitBetweenPutRecordsCallsInMilliseconds));
      
      _createStreamIfNotCreated(function(err) {
        if (err) {
          log.error(util.format('Error creating stream: %s', err));
          return;
        }
        _sendToFirehose();
      });
    }
  };
}

module.exports = twitterStreamProducer;
