OttaGraphQLEndpoint = "https://api.otta.com/graphql"
OttaLoginEndpoint = "https://api.otta.com/auth/login"
Currency = "GBP"

import requests

from logger import log as logger

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

#gql queries 
getJobsMutation = gql(open("JobsiteSniffers/ottaHelpers/refreshJobReccomendations.gql", "r").read())
jobReaction = gql(open("JobsiteSniffers/ottaHelpers/jobReaction.gql", "r").read())
jobdataQuery = gql(open("JobsiteSniffers/ottaHelpers/getJobData.gql", "r").read())
jobUpdateQuestion = gql(open("JobsiteSniffers/ottaHelpers/answerQuestion.gql", "r").read())
jobApply = gql(open("JobsiteSniffers/ottaHelpers/sendApplication.gql", "r").read())

class ottaJobsniffer:
	siteName = "otta"
	url = "https://app.otta.com/"
	jobApplicationPath = "jobs/%s/application"

	jobslist = None;

	def __init__(self, secrets):
		
		self.secrets = secrets["sniffers"]["ottaJobsniffer"]
		try:
			self.attemptLogin(self.secrets['credentials'])
		except:
			print("Could Not Log Into Otta.com, Invalid credentials Probably")
			raise Exception("LOGIN_ERROR")
			return
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
		
	ottaQuestionTypeTranslation = {
		"TEXT_AREA": "string",
		"TEXT": "string",
		"BOOLEAN": "bool",
		"DROPDOWN": "multiple choice",
		"MULTIPLE_CHOICE": "multiple choice",
		"CHECKBOXES": "multiple choice"
	}

	def setupJob(self, externalID):
		self.externalJobID = externalID
		jobData = self.getJobData(self.externalJobID)
		questions = []
		if not jobData['applicationQuestions']:
			questions.append({
				"id": None,
				"question": "Why do you want to work at %s?" % jobData['company']['urlSafeName'],
				"choices": None,
				"type": "string",
				"rawtype": "TEXT_AREA",
				"response": None
			})
		for q in jobData['applicationQuestions']:
			try:
				qtype = self.ottaQuestionTypeTranslation[q['type']]
			except:
				qtype = None
			questions.append({
				"id": q['atsId'],
				"question": q['value'],
				"type": qtype,
				"rawtype": q['type'],
				"response": None,
				"choices": list(choice["label"] for choice in q['choices']) if q['choices'] else None
			})

		return {
			"exid": self.externalJobID,
			"company": jobData['company']['urlSafeName'],
			"position": jobData['title'],
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

	def updateQuestionResponse(self, q):
		qtype= q['rawtype']

		if qtype == 'TEXT' or qtype == 'TEXT_AREA':
			return self.updateNormalQuestionResponse(q['question'], q['response'], q['id'], "stringResponse")
		if qtype == 'DROPDOWN':
			return  self.updateSingleChoiceQuestionResponse(q['question'], q['response'], q['id'], q['choices'])
		if qtype == 'MULTIPLE_CHOICE':
			return  self.updateSingleChoiceQuestionResponse(q['question'], q['response'], q['id'], q['choices'])
		if qtype == 'BOOLEAN':
			return  self.updateNormalQuestionResponse(q['question'], q['response'], q['id'], "booleanResponse")
		if qtype == 'CHECKBOXES':
			return  self.updateSingleChoiceQuestionResponse(q['question'], q['response'], q['id'], q['choices'])
		if qtype == 'DATE':
			return  None
		if qtype == 'NUMERIC':
			return  self.updateNormalQuestionResponse(q['question'], q['response'], q['id'], "decimalRespomse")
		return None

	def updateNormalQuestionResponse(self, question, response, questionId, responseTypeString):
		variables = {
			"jobId": self.externalJobID,
			"question": question,
			"atsQuestionId": questionId,
			"input": {}
		}
		variables["input"][responseTypeString] = response;
		self.client.execute(jobUpdateQuestion, variable_values=variables)
		return

	def updateSingleChoiceQuestionResponse(self, question, response, questionId, choices):
		self.client.execute(jobUpdateQuestion, variable_values={
			"jobId": self.externalJobID,
			"question": question,
			"atsQuestionId": questionId,
			"input": {
				"singleChoiceResponse": {
					"label": choices[int(response) - 1],
					"value": str(response - 1),
				}
			}
		})
		return

	def updateMultipleChoiceQuestionResponse(self, question, response, questionId, choices):
		self.client.execute(jobUpdateQuestion, variable_values={
			"jobId": self.externalJobID,
			"question": question,
			"atsQuestionId": questionId,
			"input": {
				"multipleChoiceResponse": [{
					"label": choices[int(response) - 1],
					"value": str(response - 1),
				}]
			}
		})
		return

	def sendApplication(self, applied):
		return self.client.execute(jobApply, variable_values={
			"jobId": self.externalJobID,
			"input": {
				"internal": True,
				"applied": applied,
				"clicked": True,
			}
		})
		

	def apply(self, job):
		qna = job['questions']
		errors = False
		try:
			self.sendApplication(False)
		except:
			logger.log("Allready applied to this place")
			return False


		for q in qna:
			try:
				self.updateQuestionResponse(q)
				logger.writeReportEvent(logger.questionsfile, [
					q['question'],
					q['response'],
					self.externalJobID
					])
			except Exception as e:
				logger.log('Question "%s" failed.' % q['question'])
				logger.debug(str(e))
				logger.trace()
				errors = True
		
		try:
			if errors: raise Exception("Error Updating Question Responses")
			response = self.sendApplication(True)
			if errors in response: raise Exception("Error sending application")
			return True;
		except Exception as e:
			logger.log("Job Application Failed " + str(e))
			logger.trace()
			logger.log("Complete the job application at https://app.otta.com/jobs/%s/apply" % self.externalJobID)
			return False

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