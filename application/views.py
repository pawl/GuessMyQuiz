"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from flask import request, render_template, url_for, redirect, json, jsonify
from application import app
import urllib 
import urllib2

def home():
	return redirect(url_for('guess'))

def guess():
	def column(matrix, i):
		return [row[i] for row in matrix]
	
	# based on Max M's "A little amusing Python program": https://mail.python.org/pipermail/python-list/2001-October/102669.html
	class multiChoiceGuesser:
		def __init__(self, question='', replys=()):
			self.question = question
			self.replys   = replys

		def guessedAnswer(self):
			hits = []
			for reply in self.replys:
				query = self.question + ' ' + reply
				hits.append(self.bing_search(query))
			print hits
			if all(hit == 0 for hit in hits):
				return None
			hitResult = hits.index(max(hits))
			return hitResult

		def bing_search(self, query):
			key= 'secret' # bing api key
			query = urllib.quote(query)
			# create credential for authentication
			user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
			credentials = (':%s' % key).encode('base64')[:-1]
			auth = 'Basic %s' % credentials
			url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/Composite?Sources=%27web%27&Query=%27'+query+'%27&$top=1&$format=json'
			request = urllib2.Request(url)
			request.add_header('Authorization', auth)
			request.add_header('User-Agent', user_agent)
			request_opener = urllib2.build_opener()
			response = request_opener.open(request) 
			response_data = response.read()
			json_result = json.loads(response_data)
			result_count = int(json_result['d']['results'][0]['WebTotal'])
			return result_count

	def guess(question, choices):
		mcg = multiChoiceGuesser(question, choices) 
		if mcg.guessedAnswer() is None: # mcg.guessedAnswer() can be 0
			return "Not Sure"
		else:
			return choices[mcg.guessedAnswer()]
		
	exampleOutput = [['Who created Linux?', 'Linus Torvalds','RMS','Steve Jobs','Bill Gates'],
					['What is the capital of Finland?', "Libreville", "Banjul", "Helsinki", "Dallas"]]
	
	if request.method == "POST":
		submittedData = request.json['data'] # get data from ajax request
		processedData = []
		for row in submittedData:
			if row[0]:
				result = guess('"' + row[0] + '"', row[1:])
				row.extend([result])
				processedData.append(row)
			else:
				processedData.append(row)
		return jsonify(data=processedData)
	return render_template('guess.html',exampleOutput=exampleOutput)

def warmup():
	"""App Engine warmup handler
	See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

	"""
	return ''

