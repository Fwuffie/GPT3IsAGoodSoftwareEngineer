import requests



class OttaJobsniffer:

	def __iter__(self):
		return self

	def __call__(self, secrets):
		self.secrets = secrets
		return self

	def __next__(self):
		self.getNextJob()
		if self.job:
			print("what?")
		else:
			raise StopIteration

	def getNextJob():
		print(self.secrets)
		return