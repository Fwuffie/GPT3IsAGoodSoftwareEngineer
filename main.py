import json, openai
from JobsiteSniffers.SampleJobsniffer import SampleJobsniffer

#Load Secret keys
fSecrets = open("secrets.json", "r")
secrets = json.load(fSecrets)
fSecrets.close()

openai.api_key = secrets['OpenAISecret']
