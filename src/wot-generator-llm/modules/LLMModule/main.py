from flask import Flask, request, jsonify
from cloudevents.http import from_http
from dapr.clients import DaprClient
import json
import os
import logging
#from langchain.llms import LlamaCpp
from langchain_community.llms import LlamaCpp
import time
import re
#from openai import AzureOpenAI
#logging.basicConfig(level=logging.DEBUG)

# Number of threads to use for LLM inference: pass as Env Var to override
N_THREADS = int(os.getenv('N_THREADS', os.cpu_count()))
logging.info('Number of threads for LLM inference detected or passed in: ' + str(N_THREADS))

#subscriber using Dapr PubSub
app = Flask(__name__)
app_port = os.getenv('LLM_PORT', '8601')

llmmodel = LlamaCpp(model_path="./models/phi-3-mini-4k-instruct.Q4_K_M.gguf", verbose=True, n_threads=N_THREADS)
llm_prompt = '''Use the Content to answer the Query. JSON-LD file should follow the WoT Thing Description format and include below fields:
Content: 

QUERY_CONTENT_HERE

Fields:

@context, @type, id, name, description, security

Answer:
'''

llm_wot_completion_prompt = '''Use the Content to answer the Query. JSON-LD file should follow the WoT Thing Description format and only include below fields:
Content: 

QUERY_CONTENT_HERE

Fields:

@context, @type, name, FIELD_LIST_HERE

Answer:
'''

wot_template = '''
{
  "@context": CONTEXT_HERE,
  "@type": TYPE_HERE,
  "id": ID_HERE,
  "name": NAME_HERE,
  "description": DESCRIPTION_HERE,
  "securityDefinitions": SECURITYDEFINATIONS_HERE,
  "security": SECURITY_HERE,
  "properties": PROPERTIES_HERE,
  "actions": ACTIONS_HERE
}
'''
wot_fields_list = ['CONTEXT_HERE', 'TYPE_HERE', 'ID_HERE', 'NAME_HERE', 'DESCRIPTION_HERE', 'SECURITYDEFINATIONS_HERE', 'SECURITY_HERE', 'PROPERTIES_HERE', 'ACTIONS_HERE']
keywords_list =["@context", "@type", "id",  "name", "description", "securityDefinitions", "security", "properties", "actions"]
# Mapping between placeholders and their corresponding keys in the result JSON
field_mapping = {
    'CONTEXT_HERE': '@context',
    'TYPE_HERE': '@type',
    'ID_HERE': 'id',  # Assuming 'id' might exist in future outputs
    'NAME_HERE': 'name',
    'DESCRIPTION_HERE': 'description',
    'SECURITYDEFINATIONS_HERE': 'securityDefinitions',
    'SECURITY_HERE': 'security',
    'PROPERTIES_HERE': 'properties',
    'ACTIONS_HERE': 'actions'
}

# Register Dapr pub/sub subscriptions
@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    subscriptions = [{
        'pubsubname': 'edgeragpubsub',
        'topic': 'local_llm_in_topic',
        'route': 'local_llm_in_topic_handler'
    }]
    print('Dapr pub/sub is subscribed to: ' + json.dumps(subscriptions))
    return jsonify(subscriptions)

# Dapr subscription in /dapr/subscribe sets up this route
@app.route('/local_llm_in_topic_handler', methods=['POST'])
def orders_subscriber():
    event = from_http(request.headers, request.get_data())
    user_query = str(event.data['user_query'])
    llm_type = str(event.data['llm_type'])
    print (f"received user_query: {user_query}, llm_type: {llm_type}")
    llm_prompt_prepped = llm_prompt.replace('QUERY_CONTENT_HERE',user_query)
    
    # Perform 1st time LLM inference
    inference_result_init = llm_inference(llm_prompt_prepped)
    init_generated_wot = update_wot_template(inference_result_init, wot_template)
    print (f"init_generated_wot: {init_generated_wot}")
    unfilled_fields = check_wot_completion(init_generated_wot) # unfilled_fields is a list

    # continue generate the unfilled fields iteratively
    if len(unfilled_fields) > 0:
        inter_updated_generated_wot = init_generated_wot
        unfilled_fields_mapped = [field_mapping[field] for field in unfilled_fields]
        print (f"unfilled_fields: {unfilled_fields_mapped}") #unfilled_fields: ['securityDefinitions', 'properties', 'actions']
        for unfilled_field in unfilled_fields_mapped:# exclude @context, @type, name
            # Convert unfilled_fields list to a string to replace FIELD_LIST_HERE
            if unfilled_field not in ["@context", "@type", "name"]:
                print (f"current processing unfilled_field: {unfilled_field}")
                llm_wot_completion_prompt_prepped = llm_wot_completion_prompt.replace('QUERY_CONTENT_HERE',user_query).replace('FIELD_LIST_HERE', unfilled_field)
                print (f"llm_wot_completion_prompt_prepped: {llm_wot_completion_prompt_prepped}")
                # Perform 2nd time LLM inference
                inference_result_wot_completion = llm_inference(llm_wot_completion_prompt_prepped)
                inter_updated_generated_wot = update_wot_template(inference_result_wot_completion, inter_updated_generated_wot)
                print(f"inter_updated_generated_wot: {inter_updated_generated_wot}")
        wot_file_final = inter_updated_generated_wot
    else:
        wot_file_final = init_generated_wot
    wot_file_final_complete = complete_ua_traslator_fields(wot_file_final)
    # Publish the LLM inference result
    output_message = {"inference_result": wot_file_final_complete, "llm_type": llm_type} # wot_file_final is string
    with DaprClient() as client:
        result = client.publish_event(
            pubsub_name='edgeragpubsub',
            topic_name='wot_llm_topic',
            data=json.dumps(output_message),
            data_content_type='application/json',
        )
        logging.info('Published data: ' + json.dumps(output_message))
        print (f"Published data: {json.dumps(output_message)}")
        time.sleep(1)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

def complete_ua_traslator_fields(wot_file):
    properties_value = extract_key_value(wot_file, "properties")
    try:
        # Parse the properties_value string into a dictionary
        properties_data = json.loads(properties_value)
    except json.JSONDecodeError:
        # Print a message if the input is not valid JSON and return the original value
        print("The properties_value is not a complete JSON, and cannot complete the fields for UA translator.")
        return wot_file
    
    # Iterate through each item in the properties field
    for prop_key, prop_value in properties_data.items():
        # Check if "forms" field is missing in each property
        if "forms" not in prop_value:
            # Add a default "forms" field, e.g., an empty list
            prop_value["forms"] = [
                {
                    "href": "1",
                    "op": [
                        "readproperty",
                        "observeproperty"
                    ],
                    "type": "xsd:float",
                    "pollingTime": 0
                }
            ]
            print(f'Added "forms" field to property: {prop_key}')
    
    # Convert the modified properties data back to a JSON string
    updated_properties_value = json.dumps(properties_data, indent=2)
    # Replace the original properties value with the updated one in wot_file
    updated_wot_file = re.sub(
        r'("properties"\s*:\s*)' + re.escape(properties_value), 
        r'\1' + updated_properties_value, 
        wot_file, 
        flags=re.DOTALL
    )
    return updated_wot_file
    

def update_wot_template(inference_result, wot_template_updated):
    # clean the inference_result to get json content
    cleaned_inference_result = clean_llm_response(inference_result)
    print (f"cleaned_inference_result: {cleaned_inference_result}")

    # Iterate over the wot_fields_list and replace placeholders with available data
    for field in wot_fields_list:
        print (f"current processing field: {field}, {field_mapping[field]}")
        key_value = extract_key_value(cleaned_inference_result, field_mapping[field])# field_mapping[field] map to the keyword of this field
        print (f"key_value: {key_value}")
        if key_value:
            # Replace placeholder with the corresponding field value from the result
            wot_template_updated = wot_template_updated.replace(field, key_value)
    
    print (f"wot_template_updated: {wot_template_updated}")
    return wot_template_updated
    
    
def clean_llm_response(llm_response):
    # Step 1: Find the index of the first opening curly brace '{' and the last closing curly brace '}'
    start_index = llm_response.find('{')
    end_index = llm_response.rfind('}')
    
    if start_index == -1 or end_index == -1:
        raise ValueError("No valid JSON object found in the llm response.")

    # Step 2: Extract only the valid JSON content between these indices
    json_content = llm_response[start_index:end_index+1]

    # Step 3: clean newlines and excessive spaces. Check if there are trailing commas that could invalidate the JSON
    json_content = json_content.strip()
    json_content = json_content.replace('\n', '').replace('\t', '').replace('\r', '').replace('    ', '')
    json_content = json_content.replace(',]', ']')  # Remove trailing commas in lists
    json_content = json_content.replace(',}', '}')  # Remove trailing commas in objects
    
    return json_content
    
def check_wot_completion(wot_file):
    unfilled_fields = []
    # Iterate through the wot_fields_list to check if any placeholder remains in the updated template
    for field in wot_fields_list:
        if field in wot_file:
            unfilled_fields.append(field)
    return unfilled_fields

def extract_key_value(input_string, key):
    stop_pattern = r',\s*"(?:' + r'|'.join([re.escape(keyword) for keyword in keywords_list]) + r')"'
    pattern = rf'"{key}"\s*:\s*(.*?)(?={stop_pattern}|\s*$)'  # Stop at stop_keywords prefixed by comma or end of string
    match = re.search(pattern, input_string, re.DOTALL)
    
    if match:
        # Extract the key's value
        value = match.group(1).strip()
        return value
    else:
        return None
    
def llm_inference(prompt):
    llm_response = llmmodel.invoke(prompt)
    llm_response_str=str(llm_response)
    logging.info('llm response :' + llm_response_str)
    print (f"llm response : {llm_response_str}")
    return llm_response_str

if __name__ == '__main__':
    #app.run(port=app_port)
    app.run(host='0.0.0.0', port=app_port)
