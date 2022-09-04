import json, requests, traceback

import logger as lg
global logger
logger = lg.log


workableAPI = "https://jobs.workable.com/api/v1/"

jobFilter = {
	
}

class workableJobsniffer:
	jobsStack = []

	def __init__(self, secrets):
		self.secrets = secrets
		self.jobOffset = 0
		return

	def __iter__(self):
		return self

	def __next__(self):
		#Refill queue if needed or end the itterator
		if not self.jobsStack:
			if not self.refillStack():
				raise StopIteration

		return self.formatJob( self.jobsStack.pop() )


	def formatJob(self, rawJob):
		return {
			"exid": rawJob["id"],
			"company": rawJob["company"]["title"],
			"position": rawJob["title"],
			"listing": self.generateJobListing(rawJob),
			"questions": [],
			"apply": self.apply
		}

	def refillStack(self):
		querystring = {
			"remote":"true",
			"offset":self.jobOffset,
			"query":"",
			"location": ""
			}
		response = requests.request("GET", workableAPI + "jobs", params=querystring)
		json = response.json()

		if json["jobs"]:
			self.jobsStack += json["jobs"]
			self.jobOffset += 10
			return True
		else:
			return False

		

	def generateJobListing(self, rawJob):
		return rawJob["description"]

	def apply(self, job):
		return None
