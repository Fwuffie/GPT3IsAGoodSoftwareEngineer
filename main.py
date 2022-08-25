import json, argparse
from answeringEngine import answeringEngine, user
from JobsiteSniffers.SampleJobsniffer import SampleJobsniffer
from JobsiteSniffers.OttaJobsniffer import OttaJobsniffer

#Load Secret keys
fSecrets = open("secrets.json", "r")
secrets = json.load(fSecrets)
fSecrets.close()

globalSettings;


def printDebug(text):
	if debug:
		print(text)

def specificJob(jobid):
	os = OttaJobsniffer(secrets['ottaJobsniffer'])
	u = user(secrets["userInfo"])
	ae = answeringEngine(secrets["OpenAISecret"], u)

	job = os.setupJob( jobid )
	applyToJob(ae, job)

def applyToJob(ae, job):
	print("JobID: %s" % job['exid'])
	print(job['listing'])
	for i, question in enumerate(job['questions']):
		if not question['type']: 
			print("Skipped Question: %s (%s)" % (question['question'], question['rawtype']))
			continue
		while True:
			print("Q: %s (%s)" % (question['question'], question['type']))
			questionResponse = ae.answerQuestion(question['question'], question['type'], job['listing'], choices = question['choices'])
			print("A: %s\n" % questionResponse)

			if globalSettings.automatic :
				break;

			verification = input("Is this response okay? [y]:continue | [r]:regenerate | [e]:edit - ")
			if verification.lower() == 'y':
				break;
			if verification.lower() == 'e':
				questionResponse = input("Please enter a new response: ")
				break;

		job['questions'][i]['response'] = questionResponse
	print("Applying to job...")
	job['apply'](job['questions'])
	print("Application Successful... Maybe")
	


def main():
	jobSniffers = []

	try:
		jobSniffers.append(OttaJobsniffer(secrets['ottaJobsniffer']))
	except:
		print("Error with %s Plugin" % ("OttaJobsniffer"))

	#convert Jobsniffers to iters
	jobSniffers = list(map(iter, jobSniffers))

	u = user(secrets["userInfo"])
	ae = answeringEngine(secrets["OpenAISecret"], u)

	while jobSniffers:
		#Round Robin Jobsniffers
		for jobSniffer in jobSniffers:
			try:
				job = next(jobSniffer)
			except StopIteration:
				continue
			applyToJob(ae, job)
	return

if __name__ == '__main__':
	#Parse CLI Args
	parser = argparse.ArgumentParser(description='Apply to Jobs Using GPT3.')
	parser.add_argument('-j', '--jobid', action='store', default=False, type=str, required=False, help='Applies to a single job, provided by ID')
	parser.add_argument('-a', '--automatic', action='store', default=False, type=bool, required=False, help='Applies to jobs without checking')
	globalSettings = parser.parse_args()

	if (globalSettings.jobid):
		specificJob(globalSettings.jobid)
	else:
		main()

	exit()