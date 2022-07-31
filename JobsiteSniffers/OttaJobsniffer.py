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


class OttaJobsniffer:
	def __init__(self, secrets):
		self.secrets = secrets
		self.attemptLogin(self.secrets['ottaCredentials'])
		self.transport = AIOHTTPTransport(url=OttaGraphQLEndpoint, headers={'x-csrf-token': self.csrfToken, 'content-type': 'application/json'}, cookies={'_otta_session': self.sessionToken})
		self.client = Client(transport=self.transport, fetch_schema_from_transport=True)
		return

	def __iter__(self):
		self.jobslist = self.client.execute(getJobsMutation)['refreshJobRecommendations']
		self.progress = 0
		return self

	def __next__(self):
		jobHasQuestions = False
		while not jobHasQuestions:
			jobHasQuestions = False
			self.externalJobID = self.jobslist[self.progress]['job']['externalId']
			self.internalJobID = self.jobslist[self.progress]['job']['id']
			jobData = self.getJobData(self.externalJobID)
			if jobData['acceptsInternalApplications']:
				jobHasQuestions = True
			self.client.execute(jobReaction, variable_values={
				"jobId":jobData['id'] , "direction": False
			})
			self.progress += 1
			if self.progress == len(self.jobslist): raise StopIteration
		return self.formatOttaJobData( jobData )

	def getJobData(self, id):
		queryResult = self.client.execute(jobdataQuery, variable_values={
			"externalId": id,
			"currency": Currency
		})
		return queryResult['publicJob']

	def formatOttaJobData(self, rawJobData):
		JobSpec = ""
		for spec in map(lambda t: t['value'], rawJobData['involvesBullets']):
			JobSpec += '- %s\n' % spec
		requirements = ""
		for requirement in map(lambda t: t['value'], rawJobData['requirements']):
			requirements += '- %s\n' % requirement
		joblisting =	{
							"jobListing": {
								'Company': rawJobData['company']['urlSafeName'],
								'JobTitle': rawJobData['title'],
								'Tagline': rawJobData['company']['shortDescription'],
								'Tags': list(map(lambda t: t['value'], rawJobData['company']['sectorTags'])),
								'CompanyStatement': rawJobData['company']['mission'],
								'Requirements': requirements,
								'JobSpec': JobSpec,
								'Technologies': list(map(lambda t: t['value'], rawJobData['technologiesUsed'])),
								'Location': rawJobData['company']['parsedHqAddress'],
								'Review': None,
								'Benifits': list(map(lambda t: t['value'], rawJobData['company']['otherBenefits'])),
							},
							"questions": ["Why do you want to work at %s?" % rawJobData['company']['urlSafeName']] + list(map(lambda t: t['value'], rawJobData['applicationQuestions'])),
							"apply": self.apply
						}
		return joblisting

	def attemptLogin(self, ottaCredentials):
		response = requests.request("POST", OttaLoginEndpoint, json=ottaCredentials)
		self.sessionToken = response.cookies.get_dict()['_otta_session']
		self.csrfToken = response.cookies.get_dict()['_csrf_token']
		return

	def apply(self, questionResponses):
		print(questionResponses)
		return