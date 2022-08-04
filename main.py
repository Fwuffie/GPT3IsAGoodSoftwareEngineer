import json, openai
from JobsiteSniffers.SampleJobsniffer import SampleJobsniffer
from JobsiteSniffers.OttaJobsniffer import OttaJobsniffer


#Load Secret keys
fSecrets = open("secrets.json", "r")
secrets = json.load(fSecrets)
fSecrets.close()

openai.api_key = secrets['OpenAISecret']
debug = True
manual = True

def printDebug(text):
	if debug:
		print(text)

def askGPT(primedString, tokens=256, temp=1.3):
	response = openai.Completion.create(
	  model="text-davinci-002",
	  prompt=primedString,
	  max_tokens=tokens,
	  temperature=temp
	)
	return response['choices'][0]['text'].lstrip('\n')

def primeQuestion(listing, question):
	#if question['type'] == "MULTIPLE_CHOICE":
	#	choices = "\n".join(map(lambda x: x, question['choices']))
	#	return "%s\nQ: %s (Type the number for the correct response)\n%s\n" % (listing, question['question'], choices)
	#else:
	return "%s\nQ: %s\nA: " % (listing, question['question'])

def specificJob(jobid):
	os = OttaJobsniffer(secrets)
	job = os.setupJob( jobid )
	applyToJob(job)

def applyToJob(job):
	print("JobID: %s" % job['exid'])
	print(job['listing'])
	for i, question in enumerate(job['questions']):
		if (question['type'] == 'TEXT' or question['type'] == 'TEXT_AREA'):
			while True:
				print("Q: %s (%s)" % (question['question'], question['type']))
				questionResponse = askGPT(primeQuestion(job['listing'], question))
				print("A: %s\n" % questionResponse)

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
	

# specificJob('UWZWQWF4')
# exit()

jobSniffers = [
	OttaJobsniffer(secrets)
]

#convert Jobsniffers to iters
jobSniffers = list(map(iter, jobSniffers))

while True:
	#Round Robin Jobsniffers
	for jobSniffer in jobSniffers:
		job = next(jobSniffer)
		applyToJob(job)
	continue
	