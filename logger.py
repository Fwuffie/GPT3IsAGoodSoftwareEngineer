import os, datetime, traceback, pprint


def init():
	global log;
	log = logger()

class logger:


	def __init__(self):
		self.level = "default"
		self.pp = pprint.PrettyPrinter(indent=2)

		#Create Logfile dir if it doesn't exist
		if not os.path.exists("logs"):
			os.makedirs("logs")

		#Create Log
		filename = str(datetime.date.today()) + ".log"
		self.logfile = open("logs/"+filename, "a", encoding='utf-8')

		#Create Report
		filename = str(datetime.date.today()) + ".report.csv"
		try:
			self.reportfile = open("logs/"+filename, "x")
			self.recordApplication(["JobID", "Company", "Position", "Plugin", "Url", "Success"])
		except:
			self.reportfile = open("logs/"+filename, "a", encoding='utf-8')

		filename = str(datetime.date.today()) + ".questions.csv"
		try:
			self.questionsfile = open("logs/"+filename, "x")
			self.recordApplication(["Question", "Response", "JobID"])
		except:
			self.questionsfile = open("logs/"+filename, "a", encoding='utf-8')

		#Initialise Counters
		self.counters = {}

		return

	def setLogLevel(self, level):
		self.level = level
		return

	def writeLogEvent(self, file, logmessage):
		time = datetime.datetime.today().strftime("%H:%M:%S.%f")[:-3]
		file.write( "[%s] %s\n" % (time, str(logmessage)) )
		return

	def writeReportEvent(self, file, reportArray):
		reportArray = list(map(str, reportArray))
		file.write(",".join(reportArray) + "\n")
		return

	def recordApplication(self, reportArray):
		self.writeReportEvent(self.reportfile, reportArray)
		return

	def close(self):
		self.logfile.close()
		return

	def error(self, logmessage):
		print(ansicodes.RED + logmessage + ansicodes.RST)
		self.writeLogEvent(self.logfile, "[WARN] "+ logmessage)
		return

	def log(self, logmessage):
		print(ansicodes.RST + logmessage + ansicodes.RST)
		self.writeLogEvent(self.logfile, "[LOG] "+ logmessage)
		return

	def debug(self, logmessage):
		if self.level == "debug":
			print(ansicodes.BLUE + logmessage + ansicodes.RST)
		self.writeLogEvent(self.logfile, "[DEBUG] "+ logmessage)
		return

	def trace(self):
		trace = traceback.format_exc()
		self.debug(trace)
		self.writeLogEvent(self.logfile, "[DEBUG] "+ trace)
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

class ansicodes:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RST = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'