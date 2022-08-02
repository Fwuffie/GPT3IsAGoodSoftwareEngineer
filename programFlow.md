# Program Flow

On Boot, load all sniffer plugins as itterators that return a job listing as string, array of questions and apply function.
plugins are initialised w/ 2 args, secrets for API keys and suchlike and userInfo for things like names and portfolio links.

While the program is running:
	round robin all the plugins,
	get a job listing,

	for each question
		respond to the question using gpt,
		if in manual mode:
			confirm the question response is good if in manual mode,
			allow for rewrite/regen of question response
		add question response to question object
	run apply function passing in question

job obj struct

{
	listing: String
	apply: function(questions)
	questions[]: {
		id: String
		question: String
		type: String
		response: String/None
	}
}