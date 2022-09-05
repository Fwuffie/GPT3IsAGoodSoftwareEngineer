#Start Logger
import logger as lg
lg.init()
logger = lg.log;

import json, argparse
from answeringEngine import answeringEngine, user

from JobsiteSniffers.ottaJobsniffer import ottaJobsniffer

#Load Secret keys
fSecrets = open("secrets.json", "r")
secrets = json.load(fSecrets)
fSecrets.close()

global globalSettings;


def specificJobs(jobids, sniffer):
	u = user(secrets["userInfo"])
	ae = answeringEngine(secrets["OpenAISecret"], u)

	js = loadJobSniffer(sniffer)
	if not js:
		raise Exception("Jobsniffer Plugin Not Found")

	jobids = jobids.split(",")
	jobCounter = 0
	for jid in jobids:
		try:
			jobCounter += 1
			logger.log('Applying to job %i of %i' % (jobCounter, len(jobids)))
			job = js.setupJob( jid )
			applyToJob(ae, job, js)
		except Exception as e:
			print(e)
			logger.trace()
			print("Job ID %s is invalid" % jid)


	

	

	

def applyToJob(ae, job, sniffer):
	logger.log("Applying to JobID: %s" % job['exid'])
	logger.count("applications")
	print(job['listing'])
	for i, question in enumerate(job['questions']):
		attempts = 0;
		while attempts < 4:
			print("Q: %s (%s)" % (question['question'], question['type']))
			questionResponse = ae.answerQuestion(question['question'], question['type'], job['listing'], choices = question['choices'])
			print("A: %s\n" % questionResponse)

			if not globalSettings.automatic :
				#Run User verification
				verification = input("Is this response okay? [y]:continue | [r]:regenerate | [e]:edit - ")
				if verification.lower() == 'r':
					questionResponse = None
				if verification.lower() == 'e':
					questionResponse = input("Please enter a new response: ")
					questionResponse = ae.castResponse(questionResponse, question['type'], question['choices'])
				
			if not questionResponse == None:
				break;
			attempts += 1

		job['questions'][i]['response'] = questionResponse
	print("Applying to job...")
	if job['apply'](job['questions']):
		print("Application Successful")
		logger.count("successfullApplications")
		success = True
	else:
		success = False
	logger.recordApplication([
		job['exid'],
		job['company'], 
		job['position'],
		sniffer.siteName,
		sniffer.url + (sniffer.jobApplicationPath % job['exid']),
		str(success)
		])

# Returns Itterable jobsniffer based on module name.
def loadJobSniffer(jobSnifferName):
	snifferData = secrets["sniffers"][jobSnifferName]

	if not snifferData["enabled"]:
		return False

	try:
		jsPlugin = __import__("JobsiteSniffers.%s" % jobSnifferName, globals(), locals(), [jobSnifferName], 0)
		js = getattr(jsPlugin, jobSnifferName)
		return js(snifferData)
	except Exception as e:
		print(e)
		logger.trace()
		print("Error with %s Plugin" % (jobSnifferName))
		return False

def main():
	jobSniffers = [];

	for sniffer in secrets["sniffers"]:
		js = loadJobSniffer(sniffer)
		if js:
			jobSniffers.append( iter(js) )

	u = user(secrets["userInfo"])
	ae = answeringEngine(secrets["OpenAISecret"], u)

	while jobSniffers:
		#Round Robin Jobsniffers
		for jobSniffer in jobSniffers:
			try:
				job = next(jobSniffer)
			except StopIteration:
				continue
			applyToJob(ae, job, jobSniffer)
	return

if __name__ == '__main__':
	#Parse CLI Args
	parser = argparse.ArgumentParser(description='Apply to Jobs Using GPT3.')
	parser.add_argument('-j', '--jobid', action='store', default=False, type=str, required=False, help='Applies to a single job, provided by ID')
	parser.add_argument('-a', '--automatic', action='store_true', default=False, required=False, help='Applies to jobs without checking')
	parser.add_argument('-v', action='store_true', default=False, required=False, help='Verbose Mode')

	globalSettings = parser.parse_args()

	
	if (globalSettings.v):
		logger.setLogLevel("debug")

	# Apply to specific jobs
	if (globalSettings.jobid):
		specificJobs(globalSettings.jobid, "ottaJobsniffer")
		exit();

	try:
		main()
	except KeyboardInterrupt:
		print("Exiting Gracefully.")
	except Exception as e:
		logger.log(e)
		logger.trace()
	finally:
		logger.log("Applied to %i Jobs, %i failed applications" % (logger.getCount("successfullApplications"), logger.getCount("applications") - logger.getCount("successfullApplications")))
		logger.close()
		exit()