READ ME!

This application was developed using NodeJS version 10.16.0.

See https://aws.amazon.com/blogs/big-data/building-a-near-real-time-discovery-platform-with-aws/ to learn how to set up the AWS components used in this application.

To configure:

	- Execution requires AWS to be pre-configured before excecution (i.e. ".aws/credentials" folder exists in user's home directory). See AWS CLI set up instructions for more info.
	- Create a file called "C:\temp\config.js" that matches the example sample_config.js provided.  Populate this new config.js file with your appropriate AWS and Twitter information.

To execute:
	
	- in a Node JS terminal and in the same folder location as the script, type "node twitter_search_producer_app" 
	- an output log will be produced in the local script directory called "application.log".
	
	
