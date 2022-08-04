OttaGraphQLEndpoint = "https://api.otta.com/graphql"
OttaLoginEndpoint = "https://api.otta.com/auth/login"
Currency = "GBP"

import requests

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

#gql queries 
getJobsMutation = gql(open("JobsiteSniffers/ottaHelpers/refreshJobReccomendations.gql", "r").read())
jobReaction = gql(open("JobsiteSniffers/ottaHelpers/jobReaction.gql", "r").read())
jobdataQuery = gql(open("JobsiteSniffers/ottaHelpers/getJobData.gql", "r").read())
jobUpdateQuestion = gql(open("JobsiteSniffers/ottaHelpers/answerQuestion.gql", "r").read())
jobApply = gql(open("JobsiteSniffers/ottaHelpers/sendApplication.gql", "r").read())

class OttaJobsniffer:
	jobslist = None;

	def __init__(self, secrets):
		self.secrets = secrets
		self.attemptLogin(self.secrets['ottaCredentials'])
		self.transport = AIOHTTPTransport(url=OttaGraphQLEndpoint, headers={'x-csrf-token': self.csrfToken, 'content-type': 'application/json'}, cookies={'_otta_session': self.sessionToken})
		self.client = Client(transport=self.transport, fetch_schema_from_transport=True)
		return

	def __iter__(self):
		return self

	def __next__(self):
		while True:
			#Update joblist if needed
			if not self.jobslist:
				self.jobslist = self.client.execute(getJobsMutation)['refreshJobRecommendations']
				if not self.jobslist:
					raise StopIteration #Raise Error if out of jobs
			#Pop next Job From Stack
			job = self.jobslist.pop()['job']
			#Pop Job from Otta
			self.client.execute(jobReaction, variable_values={
				"jobId":job['id'] , "direction": False
			})
			#Check if it can be applied to
			if job['acceptsInternalApplications']:
				self.client.execute(jobReaction, variable_values={
					"jobId":job['id'] , "direction": True
				})
				break;
		return self.setupJob(job['externalId'])
		

	def setupJob(self, externalID):
		self.externalJobID = externalID
		jobData = self.getJobData(self.externalJobID)
		questions = []
		if not jobData['applicationQuestions']:
			questions.append({
				"id": None,
				"question": "Why do you want to work at %s?" % jobData['company']['urlSafeName'],
				"type": "TEXT_AREA",
				"response": None
			})
		for q in jobData['applicationQuestions']:
			questions.append({
				"id": q['atsId'],
				"question": q['value'],
				"type": q['type'],
				"response": None,
				"choices": q['choices']
			})

		return {
			"exid": self.externalJobID,
			"listing": self.generateJobListing(jobData),
			"questions": questions,
			"apply": self.apply
		}

	def getJobData(self, id):
		queryResult = self.client.execute(jobdataQuery, variable_values={
			"externalId": id,
			"currency": Currency
		})
		return queryResult['publicJob']


	def attemptLogin(self, ottaCredentials):
		response = requests.request("POST", OttaLoginEndpoint, json=ottaCredentials)
		self.sessionToken = response.cookies.get_dict()['_otta_session']
		self.csrfToken = response.cookies.get_dict()['_csrf_token']
		return

	def updateQuestionResponse(self, question, response, questionId):
		self.client.execute(jobUpdateQuestion, variable_values={
			"jobId": self.externalJobID,
			"question": question,
			"atsQuestionId": questionId,
			"input": {
				"stringResponse": response
			}
		})
		return

	def sendApplication(self, applied):
		self.client.execute(jobApply, variable_values={
			"jobId": self.externalJobID,
			"input": {
				"internal": True,
				"applied": applied,
				"clicked": True,
			}
		})
		return

	def apply(self, qna):
		errors = False
		self.sendApplication(False)
		for q in qna:
			try:
				self.updateQuestionResponse(q['question'], q['response'], q['id'])
			except Exception as e:
				print('Question "%s" failed.' % q['question'])
				errors = True
		if not errors: self.sendApplication(True)
		else: print("Complete the job application at https://app.otta.com/jobs/%s/apply" % self.externalJobID)
		return

	
	def generateJobListing(self, rawJobData):
		JobSpec = ""
		for spec in map(lambda t: t['value'], rawJobData['involvesBullets']):
			JobSpec += '- %s\n' % spec
		requirements = ""
		for requirement in map(lambda t: t['value'], rawJobData['requirements']):
			requirements += '- %s\n' % requirement

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

Q: Provide a link to a portfolio or website.
A: portfolio.nyan.ca

''' % (
		rawJobData['title'],
		rawJobData['company']['urlSafeName'],
		rawJobData['company']['shortDescription'],
		", ".join(list(map(lambda t: t['value'], rawJobData['company']['sectorTags']))),
		", ".join(list(map(lambda t: t['value'], rawJobData['technologiesUsed']))),
		rawJobData['company']['mission'],
		JobSpec,
		requirements,
	)
		return jobListingString