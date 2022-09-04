# Creating A Plugin

To create a plugin add a {pluginName}.py file to the Jobsitesniffers folder.
That file must contain a class with the name {pluginName}

the values stored in secret.json with the key {pluginName} are passed into the class initialiser

The class must be an itterable, where each itterator returns a dict with the following format.

```
{
	"exid": An ID To reference the job
	"company": The Company of the job (Used for generating Logs)
	"position": The Position Being applied too (Used for generating Logs)
	"listing": A String that describes the whole job listing, that will be sent to GPT
	"questions": A List of Questions (see question structure)
	"apply": A function that applys to the job being described
}
```

questions describe questions that are being asked by the job application, they have the following format.

```
{
	"question": A String containing the question that will be asked to gpt.
	"choices": An optional key for questions with multiple choice answers
	"type": one of; string, int, bool, multiple choice.
	"response": None,
}
```

the same question object is sent back as part of the apply function, so addtional keys can be used to store additional question data required to apply e.g. tracking a question ID number that isn't required to generate a response.

The Apply function returns the full job object, with the questions\[\]->response updated to contain a response with the type specified. Multiple choice are returned with the index of the choice.