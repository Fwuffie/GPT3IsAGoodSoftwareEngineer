import json, requests, traceback
import html2text
from logger import ansicodes


import logger as lg
global logger
logger = lg.log


workableAPI = "https://jobs.workable.com/api/v1/"

jobFilter = {
	
}

class workableJobsniffer:
	jobsStack = []

	def __init__(self, secrets):
		self.secrets = secrets["sniffers"]["workableJobsniffer"]
		self.applicantName = secrets["userInfo"]["firstname"]
		self.jobOffset = 10
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
			"questions": self.getQuestions(rawJob),
			"apply": self.apply
		}

	def refillStack(self):
		querystring = {
			"remote":"true",
			"offset":self.jobOffset,
			"query":"Software Engineer | Web Developer | Devops",
			"location": "United Kingdom"
			}
		response = requests.request("GET", workableAPI + "jobs", params=querystring)
		json = response.json()

		if json["jobs"]:
			self.jobsStack += json["jobs"]
			self.jobOffset += 10
			return True
		else:
			return False

	def uploadResume(self, jobID):
		uploadUrl = workableAPI + "jobs/" + jobID + "/form/upload/resume?contentType=application\%2Fpdf"

		resume = open("resume.pdf", "rb")
		files = {'file': resume}

		getHeaders = {"Content-Type": "application/pdf"}
		response = requests.request("GET", uploadUrl, headers=getHeaders)
		responseJson = response.json()

		payload = responseJson["uploadPostUrl"]["fields"]
		payload["Content-Type"] = "application/pdf"
		awsresponse = requests.request("POST", responseJson["uploadPostUrl"]["url"], data=payload, files=files)

		return responseJson["downloadUrl"]

	def apply(self, job):
		applicationURL = workableAPI + "jobs/" + job["exid"] + "/apply"

		body = {"candidate": []}

		for question in job["questions"]:
			if question["type"]:
				body["candidate"].append({
					"name": question["id"],
					"value": question["response"]
				})
			else:
				#Check If Looking For Known File
				if question["rawtype"] == "file":
					if question["id"] == "resume":
						body["candidate"].append({
							"name": question["id"],
							"value": {
								"url": self.uploadResume(job["exid"]),
								"name": "resume.pdf"
							}
							
						})
						continue
				#Check if required
				if question["required"]:
					raise Exception("Missing Type For Required Field %s on question %s" % (question["rawtype"], question["label"]))

		headers = {"Content-Type": "application/json"}
		response = requests.request("POST", applicationURL, headers=headers, json=body)
		logger.debug(response.text)
		return True	

	questionTypeTranslation = {
		"paragraph": "string",
		"boolean": "bool",
		"text": "string",
		"email": "string",
		"phone": "string",
		"multiple": "multiple choice",
		"group": None,
		"file": None
	}

	def getQuestions(self, rawJob):
		questionsURL = workableAPI + "jobs/" + rawJob["id"] + "/form"
		response = requests.request("GET", questionsURL)
		responseJson = response.json()

		questions = []

		for section in responseJson:
			for question in section["fields"]:
				qresponse = None
				if question["id"] == "summary":
					question["label"] = "Create a first person personalised summary of a person who is applying to this position."
				if question["id"] == "cover_letter":
					question["label"] = "Create a cover letter for this position from %s." % self.applicantName
				if "onlyTrueAllowed" in question:
					qresponse = True
				questions.append({
					"id": question["id"],
					"question": question["label"] if "label" in question else None,
					"choices": list(map(lambda x: x["value"], question["options"])) if "options" in question else None,
					"rawChoices": question["options"] if "options" in question else None,
					"type": self.questionTypeTranslation[question["type"]],
					"rawtype": question["type"],
					"response": qresponse,
					"required": question["required"]
				})

		return questions

	def generateJobListing(self, rawJob):
		h = html2text.HTML2Text()
		h.ignore_links = True

		return f"""
{rawJob["title"]} at {rawJob["company"]["title"]}
==============================================================================
{h.handle(rawJob["description"])}

{('REQUIREMENTS:' + h.handle(rawJob["requirementsSection"])) if rawJob["requirementsSection"] else ""}

Application
============
"""

