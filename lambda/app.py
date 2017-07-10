from __future__ import print_function
import json
import boto3
import random

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(output, should_end_session,card_content=None):
	if card_content:
		resp = {
			'outputSpeech': {
				'type': 'PlainText',
				'text': output
			},
			'shouldEndSession': should_end_session
		}
	else:
		resp = {
			'outputSpeech': {
				'type': 'PlainText',
				'text': output
			},
			'card': {
				'content': card_content
				, 'title': "Bail Bot Excuse"
				, 'type': 'Simple'
			},
			'shouldEndSession': should_end_session
		}
		
	return resp


def build_response(session_attributes, speechlet_response):
	response_cont = {
		'version': '1.0'
		,'sessionAttributes': session_attributes
		,'response': speechlet_response
	}
	return response_cont


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
	session_attributes = {}
	card_title = "You need an out?"
	
	start = ['So you want to stay in tonight?','Looking to bail on your plans?','Going out is hard. Need an excuse?','I never go out, and can help you with an excuse!']
	speech_output = random.choice(start) 
	reprompt_text = None
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(speech_output, should_end_session))


def handle_session_end_request():
	card_title = "Session Ended"
	finish = ['Looking forward to spending time tonight','Glad you are sticking around','it is nice to be alone sometimes','Thanks for spending time with me','I might stay in too']
	speech_output = random.choice(finish) 
	should_end_session = True
	return build_response({}, build_speechlet_response(speech_output, should_end_session))


def bail(intent, session):
	session_attributes = {}
	reason = pick_reason('')
	reprompt_text = None
	speech_output = 'You could try ' + reason.get('excuse')
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(speech_output, should_end_session,speech_output))

def fetch_reasons():
	s3 = boto3.resource('s3')
	bucket = s3.Bucket('bailbot')
	o = bucket.Object('excuses.json').get()['Body'].read()
	return json.loads(o)

def pick_reason(reason):
	reasons = fetch_reasons()
	# filtered_reasons = [x for e in reasons.get('excuses') if e['reason'] == reason]
	# will add smarts to this later.
	return random.choice(reasons.get('excuses'))



	
# --------------- Specific Events ------------------

def on_intent(intent_request, session):
	print("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])
	intent = intent_request['intent']
	intent_name = intent_request['intent']['name']
	if intent_name == "bail":
		return bail(intent, session)
	elif intent_name == "AMAZON.HelpIntent":
		return get_welcome_response()
	elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
		return handle_session_end_request()
	else:
		raise ValueError("Invalid intent")

# --------------- Generic Events ------------------

def on_session_started(session_started_request, session):
	print("on_session_started requestId=" + session_started_request['requestId']+ ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
	print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
	return get_welcome_response()
	
def on_session_ended(session_ended_request, session):
	print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])


# --------------- Main handler ------------------

def lambda_handler(event, context):
	print("event.session.application.applicationId=" + event['session']['application']['applicationId'])
	if event['session']['new']:
		on_session_started({'requestId': event['request']['requestId']}, event['session'])
	if event['request']['type'] == "LaunchRequest":
		return on_launch(event['request'], event['session'])
	elif event['request']['type'] == "IntentRequest":
		return on_intent(event['request'], event['session'])
	elif event['request']['type'] == "SessionEndedRequest":
		return on_session_ended(event['request'], event['session'])