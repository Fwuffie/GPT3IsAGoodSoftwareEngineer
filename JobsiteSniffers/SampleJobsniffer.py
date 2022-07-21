from faker import Faker
import random
fake = Faker()

tecnologiesSample = ["AWS","Python","Java","Kubernetes","Docker","React","JavaScript","Go","Terraform","Linux","TypeScript","SQL","Ruby","C++","GCP","Kafka","Git","MySQL","Azure","Redis","Postgres","Node.js","Jenkins","GraphQL","Ansible","C#","Haskell","jQuery","PHP","REST API","Windows"]
tagsSample = ["SaaS", "B2C", "Enterprise", "Marketplace", "eCommerce", "Analytics", "Marketing", "Retail", "Mobile", "Financial Services", "Data Analysis", "Machine Learning", "Big data", "HR", "Lifestyle", "Cloud Computing", "Personal health", "Investing", "Community", "API", "Content", "Learning", "Digital Media", "Recruitment", "Consumer Goods", "Advertising", "Social Impact", "Banking", "Business Intelligence", "MedTech", "Video", "Personal finance", "Property", "Transport"]
benifitsSample = ["Health insurance",
"Paid time off (PTO) such as sick days and vacation days",
"Flexible and remote working options",
"Life insurance",
"Short-term disability",
"Long-term disability",
"Retirement benefits or accounts",
"Financial planning resources",
"Professional development",
"Fitness or healthy lifestyle incentives",
"Employee assistance programs (mental and emotional wellbeing)",
"Identity theft protection",
"Childcare benefits",
"Student loan repayment benefits",
"Home office improvement incentives for remote workers",
"Sign-on bonuses"]

class SampleJobsniffer:
	jobsToReturn = 5

	def __iter__(self):
		self.count = 1
		return self

	def __next__(self):
		if self.count <= self.jobsToReturn:
			self.count += 1
			self.jobObj = {
				'jobListing': self.generateJobListing()
			}
			self.jobObj['questions'] = self.generateQuestions()
			self.jobObj['apply'] = self.apply()
			return self.jobObj
		else:
			raise StopIteration

	def apply(self):
		return

	def generateJobListing(self):
		requirements = ""
		for i in range(0,random.randrange(2,7)):
			requirements += '- %s /n' % fake.bs()
		joblisting =	{
							'Company': fake.company(),
							'JobTitle': fake.job(),
							'Tagline': fake.catch_phrase(),
							'Tags': fake.random_choices(elements=tagsSample,length=random.randrange(2,5)),
							'CompanyStatement': fake.bs(),
							'Requirements': requirements,
							'JobSpec': "",
							'Technologies': fake.random_choices(elements=tecnologiesSample,length=random.randrange(2,6)),
							'Location': fake.city(),
							'Review': "",
							'Benifits': fake.random_choices(elements=tecnologiesSample,length=random.randrange(2,6)),
						}
		return joblisting

	def generateQuestions(self):
		print(self.jobObj)
		questions = ["Why do you want to work at %s?" % (self.jobObj['jobListing']['Company'])] 
		return questions