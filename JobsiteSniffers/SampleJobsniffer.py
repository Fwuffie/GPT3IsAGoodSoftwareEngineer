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
requirementsSample = [
"2+ years experience with modern backend technologies",
"A desire to work on big complex projects with lots of creative freedom",
"A passion for shipping high-quality products",
"An interest in the crypto space, and a love for building tools that help users navigate the web3 world",
"Empathetic and love to help your teammates grow",
"You are proficient in TypeScript, JavaScript, or similar",
"You have experience with GCP and Terraform",
"You have a good understanding of database structures and can write some SQL",
"You’ve written integrations against 3rd party systems and APIs",
"You’ve built frontend UIs and have an understanding of accessibility",
"You have an interest in using data and engineering to solve large-scale consumer problems, as well as a good sense for building products that consumers want to use",
"You have at least 2 years of experience building distributed systems in Node.js using Typescript or JavaScript",
"You care deeply about building reliable, well-tested systems",
"You are great at explaining complicated technical concepts clearly",
"Have an understanding of the principles of computer science",
"Proficiency in building applications using React and TypeScript in production",
"Write well-structured and high-quality code that’s easily maintainable by others",
"Self-driven and capable of working with minimal supervision"
]


class sampleJobsniffer:
	jobsToReturn = 1

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
		JobSpec = ""
		for i in range(0,random.randrange(5,10)):
			JobSpec += '- %s\n' % fake.bs()
		requirements = ""
		for i in range(0,random.randrange(5,10)):
			requirements += '- %s\n' % fake.random_choices(elements=requirementsSample, length=1)[0]
		joblisting =	{
							'Company': fake.company(),
							'JobTitle': fake.job(),
							'Tagline': fake.catch_phrase(),
							'Tags': fake.random_choices(elements=tagsSample,length=random.randrange(2,5)),
							'CompanyStatement': fake.bs(),
							'Requirements': requirements,
							'JobSpec': JobSpec,
							'Technologies': fake.random_choices(elements=tecnologiesSample,length=random.randrange(2,6)),
							'Location': fake.city(),
							'Review': "",
							'Benifits': fake.random_choices(elements=tecnologiesSample,length=random.randrange(2,6)),
						}
		return joblisting

	def generateQuestions(self):
		questions = ["Why do you want to work at %s?" % (self.jobObj['jobListing']['Company'])] 
		return questions