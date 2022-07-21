import json, openai
from JobsiteSniffers.SampleJobsniffer import SampleJobsniffer

#Load Secret keys
fSecrets = open("secrets.json", "r")
secrets = json.load(fSecrets)
fSecrets.close()

openai.api_key = secrets['OpenAISecret']

def askGPT(primedString):
	response = openai.Completion.create(
	  model="text-davinci-002",
	  prompt=primedString,
	  max_tokens=256,
	  temperature=1.5
	)
	return response['choices'][0]['text']

def formatJobPostingSoftwareDev(joblisting):
	jobListingString = '''
Job Listing
==================================
Position: %s
Company: %s - %s
Tags: %s
Technologies: %s

%s

What the job involves
================
%s

Who you are
============
%s

Application
============''' % (
		joblisting['JobTitle'],
		joblisting['Company'],
		joblisting['Tagline'],
		", ".join(joblisting['Tags']),
		", ".join(joblisting['Technologies']),
		joblisting['CompanyStatement'],
		joblisting['JobSpec'],
		joblisting['Requirements'],
	)

	return jobListingString;

def primeQuestion(listing, question):
	return "%s\nQ: %s\nA: " % (listing, question)

for job in SampleJobsniffer():
	listing = formatJobPostingSoftwareDev(job['jobListing'])
	listing = primeQuestion(listing, job['questions'][0])
	print(listing)
	print(askGPT(listing))

