import os, datetime


def init():
	global log;
	log = logger()

class logger:

	def __init__(self):
		self.level = "default"

		#Create Logfile dir if it doesn't exist
		if not os.path.exists("logs"):
			os.makedirs("logs")

		#Create Log
		filename = str(datetime.date.today()) + ".log"
		self.logfile = open("logs/"+filename, "a")

		#Create Report
		filename = str(datetime.date.today()) + ".report.csv"
		try:
			self.reportfile = open("logs/"+filename, "x")
			self.recordApplication(["JobID", "Company", "Position", "Plugin", "Url", "Success"])
		except:
			self.reportfile = open("logs/"+filename, "a")

		filename = str(datetime.date.today()) + ".questions.csv"
		try:
			self.questionsfile = open("logs/"+filename, "x")
			self.recordApplication(["Question", "Response", "JobID"])
		except:
			self.questionsfile = open("logs/"+filename, "a")

		#Initialise Counters
		self.counters = {}

		return

	def setLogLevel(self, level):
		self.level = level
		return

	def writeLogEvent(self, file, logmessage):
		time = datetime.datetime.today().strftime("%H:%M:%S.%f")[:-3]
		file.write( "[%s] %s\n" % (time, logmessage) )
		return

	def writeReportEvent(self, file, reportArray):
		file.write(",".join(reportArray) + "\n")
		return

	def recordApplication(self, reportArray):
		self.writeReportEvent(self.reportfile, reportArray)
		return

	def close(self):
		self.logfile.close()
		return

	def log(self, logmessage):
		print(logmessage)
		self.writeLogEvent(self.logfile, logmessage)
		return

	def debug(self, logmessage):
		if self.level == "debug":
			print(logmessage)
		self.writeLogEvent(self.logfile, "[DEBUG] "+ logmessage)
		return

	def getCount(self, label):
		return self.counters[label] if label in self.counters else 0

	def count(self, label):
		if label in self.counters:
			self.counters[label] += 1
		else:
			self.counters[label] = 1
		self.writeLogEvent(self.logfile, "Count: %s	(%i)" % (label, self.counters[label]))
		return self.counters[label]