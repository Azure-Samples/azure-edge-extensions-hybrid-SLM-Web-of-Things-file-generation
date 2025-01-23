from flask import Flask, request, jsonify
from dapr.clients import DaprClient
import json
import os
import logging
import time
import uuid
from openai import AzureOpenAI

from function.openai_helper.config import *

#subscriber using Dapr PubSub
app = Flask(__name__)
app_port = os.getenv('ROUTER_PORT', '8702')

system_msg = """
You are an AI assistant that helps people find information. first, you can search the private data content to get the answer, if there's no available information, then check your base model to return the reasonable information.
"""
client = AzureOpenAI(
                api_key = AZURE_OPENAI_API_KEY,
                api_version = AZURE_OPENAI_API_VERSION,
                azure_endpoint= AZURE_OPENAI_ENDPOINT,
            )
gpt_prompt = '''Use the Content to answer the Query.
Content: 

QUERY_CONTENT_HERE

Answer:
'''

def classify_question(question):
    categories = ["WoT", "general"]
    prompt_text = f"For the below text, provide one single label each from the following categories:\n- Category: {', '.join(categories)}\n\nThe system should analyze the question and identify if it is related to generate a Web of Thing contents like Web of Thing json-ld file, Web of Thing fields. If so, the system should respond with 'WoT'. For all other questions, the system should respond with 'general'. Examples: Question: can you create a json-ld web of things file that describes an ONVIF device? Category: WoT Question: How can I troubleshoot the connection issue? Category: general\n\nQuestion: {question}\nCategory:"
    text = openAI_ChatCompletion(prompt_text)
    # Response provided by GPT-3.5
    return text

def openAI_ChatCompletion(query):
    response = client.chat.completions.create(
            model = CHAT_MODEL,# model = "deployment_name".
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": system_msg
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
    text = response.choices[0].message.content
    return text

def publish_message_local(data_json):
    with DaprClient() as client:
        result = client.publish_event(
            pubsub_name='edgeragpubsub',
            topic_name='local_llm_in_topic',
            data=json.dumps(data_json),
            data_content_type='application/json',
        )
        print (f"Published data: {json.dumps(data_json)}")
        logging.info('Published data: ' + json.dumps(data_json))
        time.sleep(1)


# API for receiving user input from the frontend web app
@app.route('/webpublish', methods=['POST'])
def publish():
    data = request.json
    user_query = data.get('user_query')
    selected_llm = data.get('selected_llm')

    if user_query:
            # mapping of llm_to_use
        if selected_llm == "edge-phi3-mini" or selected_llm == "gpt-3.5-turbo":
            llm_to_use = selected_llm
        else:
            category = classify_question(user_query) 
            if category == "WoT":
                llm_to_use = "edge-phi3-mini"
            else:
                llm_to_use = "gpt-3.5-turbo"
            print (f"category: {category}, llm_to_use: {llm_to_use}")

        # call LLM for inference
        if llm_to_use == "edge-phi3-mini": 
            # call local LLM
            local_llm_query_json = {'user_query': user_query, 'llm_type': llm_to_use}
            publish_message_local(local_llm_query_json)
        else:
            # call GPT3.5-turbo
            gpt_prompt_prepped = gpt_prompt.replace('QUERY_CONTENT_HERE',user_query)
            gpt_response = openAI_ChatCompletion(gpt_prompt_prepped)
            
            gpt_output_message = {"inference_result": gpt_response, "llm_type": llm_to_use}
            with DaprClient() as client:
                result = client.publish_event(
                    pubsub_name='edgeragpubsub',
                    topic_name='wot_llm_topic',
                    data=json.dumps(gpt_output_message),
                    data_content_type='application/json',
                )
                print (f"Published data gpt: {json.dumps(gpt_output_message)}")
                logging.info('Published data: ' + json.dumps(gpt_output_message))
                time.sleep(1)
        return jsonify({'status': 'success', 'category': category, 'llm_to_use': llm_to_use})

    return jsonify({'status': 'error', 'message': 'Invalid user input'})


if __name__ == '__main__':
    #app.run(port=app_port)
    app.run(host='0.0.0.0', port=app_port)

