import json, openai
from JobsiteSniffers.SampleJobsniffer import SampleJobsniffer

#Load Secret keys
fSecrets = open("secrets.json", "r")
secrets = json.load(fSecrets)
fSecrets.close()

openai.api_key = secrets['OpenAISecret']

# print(openai.Completion.create(
#   model="text-davinci-002",
#   prompt="Say this is a test",
#   max_tokens=6,
#   temperature=0.9
# ))

for job in SampleJobsniffer():
	print(json.dumps(job, indent=2))