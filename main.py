import json, openai
from JobsiteSniffers.SampleJobsniffer import SampleJobsniffer
from JobsiteSniffers.OttaJobsniffer import OttaJobsniffer


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
============
Q: What is your name?
A: Lily Page

Q: Provide a link to your github.
A: github.com/fwuffie

Q: Which country are you from?
A: Scotland, UK

''' % (
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

def specificJob(jobid):
	os = OttaJobsniffer(secrets)
	job = os.formatOttaJobData( os.getJobData(jobid) )
	print(job)
	verification = ""
	while not (verification.lower() == "y" or verification.lower == "yes"):
		listing = formatJobPostingSoftwareDev(job['jobListing'])
		print(listing)
		questionResponses = []
		for question in job['questions']:
			print("Q: %s" % question)
			questionResponse = askGPT(primeQuestion(listing, question))
			print("A: %s\n" % questionResponse)
			questionResponses.append(questionResponse)
		verification = input("Are these responses okay? (Y/N)")
		if (verification.lower() == "y" or verification.lower == "yes"):
			job['apply'](questionResponses)

specificJob("eEVrb1Np")
quit()

for job in OttaJobsniffer(secrets):
	verification = ""
	while not (verification.lower() == "y" or verification.lower == "yes"):
		listing = formatJobPostingSoftwareDev(job['jobListing'])
		print(listing)
		questionResponses = []
		for question in job['questions']:
			print("Q: %s" % question)
			questionResponse = askGPT(primeQuestion(listing, question))
			print("A: %s\n" % questionResponse)
			questionResponses.append(questionResponse)
		verification = input("Are these responses okay? (Y/N)")
		if (verification.lower() == "y" or verification.lower == "yes"):
			job['apply'](questionResponses)