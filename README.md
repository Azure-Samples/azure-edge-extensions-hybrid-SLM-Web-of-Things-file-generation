# Hybrid LLM Application for Web-of-Things (WoT) File Generation

![architecture](./images/Design%20of%20Asset%20onboarding%20automation%20with%20LLM.png)



## LLM Router(llm-based classifier):
LLM router for auto selecting edge LLM or OpenAI for WoT generation

Query to generate a WoT file. route to local LLM (phi3-mini)
Other query: route to Azure OpenAI GPT.

![LLM module design](./images/redesign%20logic%20of%20generating%20WoT%20with%20Phi3-mini%20to%20address%20SLM's%20limitatio.png)

## Test response quality of generating WoT files with different local LLM and openAI model.
Using Prompt that same as in Bill's Bingchat experiment: "As an expert in the ONVIF specification and with your deep knowledge of the Web of Things specification, can you create a json-ld web of things file that describes an ONVIF device?"

Phi2 on edge: "Sure, I'd be happy to help. However, as an AI language model, I do not have access to specific information about any particular ONVIF or Web of Things devices. Can you provide me with some details about the specific device or devices you would like me to describe?"

Phi3-mini on edge: " The following is my attempt:
@context {http://www.w3.org/ns/wot/core#Device}
{ # This represents the JSON object for our hypothetical Onvif Camera Device, identified by its unique ID (UUID). Replace 'your_uuid' with an actual UUID of your device if available:
@id "https://www.w3.org/ns/wot/devices/your_uuid"; # Unique identifier for the Onvif Camera Device
@type "http://www.onvif.org/ver10/device/~xmlschema#OnvifCameraDevice" # The type of device, an ONVIF camera in this case:
name "{your_camera_model}"; # Name or model of the Camera Device
manufacturer "Your Company Inc.";
@type "http://www.w3.org/2 Employee Performance Analysis Using Machine Learning Techniques

Employee performance analysis is an essential function for any organization, as it helps to identify high-performing employees and provide feedback that can drive improvements in productivity.
"

GPT3.5: "Certainly! I can help you create a JSON-LD Web of Things file that describes an ONVIF device. However, please note that as an AI assistant, I don't have access to private data or specific knowledge about ONVIF devices. I can provide general information based on my training data.

Here's an example of how you can structure a JSON-LD Web of Things file for an ONVIF device:

{
  "@context": [
    "https://www.w3.org/2019/wot/td/v1",
    {
      "onvif": "http://www.onvif.org/ver10/schema"
    }
  ],
  "@type": "Thing",
  "title": "ONVIF Device",
  "securityDefinitions": {
    "basic_sc": {
      "scheme": "basic",
      "in": "header"
    }
  },
  "security": [
    "basic_sc"
  ],
  "properties": {
    "manufacturer": {
      "type": "string",
      "readOnly": true,
      "description": "The manufacturer of the ONVIF device"
    },
    "model": {
      "type": "string",
      "readOnly": true,
      "description": "The model of the ONVIF device"
    },
    "firmwareVersion": {
      "type": "string",
      "readOnly": true,
      "description": "The firmware version of the ONVIF device"
    },
    "serialNumber": {
      "type": "string",
      "readOnly": true,
      "description": "The serial number of the ONVIF device"
    }
  },
  "actions": {
    "reboot": {
      "description": "Reboots the ONVIF device",
      "safe": false
    }
  }
}
Please note that this is a basic example and you may need to customize it further based on your specific ONVIF device's capabilities and features."

Prompt: "As an expert in edge device specification and with your deep knowledge of the Web of Things specification, can you create a json-ld web of things file that describes an device Siemens Sentron PAC4200?
No need any word explaination, just give me a pure Json-ld file."

Phi3-mini on edge: "To fulfill this request accurately and in compliance with current industry standards for the Web of Things (WoT), I would require access to specific details about the Siemens Sentron PAC4200 device that pertains to its functionality, data modeling requirements, sensor types it might contain or interact with within a WoT context.
Without having this information readily available and considering privacy concerns (as well as not knowing if there are any proprietary specifications for such devices), I can provide you an example template that demonstrates how to structure JSON-LD in the spirit of W3C's recommendations:
{
"@context": "https://schema.org", // WoT context specification, see https://www.w3.org/TR/wot-primer/#section-4 for more details on this format and examples that comply with the WOT standards; you will need to replace it's content accordingly
"@graph": [
{
"id": "#Siemens_PAC4200", // Unique identifier of the device, use a stable UUID or other unique identifiers if applicable. It is important that this ID"

Prompt for ONVIF camera device TP-Link VIGI C240 4MP Full-Color Dome Network Camera. and include Siemens SENTRON PAC4200 WoT file as an example.
Response: not following Json but describe how to change from Siemens SENTRON PAC4200 WoT file to ONVIF camera file. Also halfway done.

My final prompt to test local LLM: As an expert in edge device specification and with your deep knowledge of the Web of Things specification, can you generate a JSON-LD web of things file that describes a device Siemens SENTRON PAC4200?
JSON-LD file should follow the WoT Thing Description format and include below fields:
{
"@context":
"id":
"securityDefinitions":
"security":
"@type":
"title":
"description":
"properties":
"actions":
}

Phi3-mini on edge: "Example of JSON-LD file for the Siemens PAC4200 device:
{
"@context":"http://schema.org/",
"@type":"ThingDescription","id":"https://www.siemens.com/us/en/products/electronics/energy/power_converters-inverter_and_chargers/_516342078965a6b3fef54dfe/?lang=en",
"securityDefinitions": { },
"@type":"ThingDescription","id":"https://www.siemens.com/us/en/products/electronics/energy/power_converters-inverter_and_chargers/_516342078965a6b3fef54dfe/?lang=en",
"name":"Siemens SENTRON PAC4200","description":{ },"properties":{"manufacturer":{"@type":"Organization"},"modelNumber":{"@type":"Text"},"wattage":{"@type":"Integer"} },"actions":[{ "@type":"
"

Prompt for Onvif camera: "As an expert in edge device specification and with your deep knowledge of the Web of Things specification, Please generate a JSON-LD web of things file that describes a device ONVIF camera device TP-Link VIGI C240 4MP Full-Color Dome Network Camera.
JSON-LD file should follow the WoT Thing Description format and include below fields:
{
"@context":
"id":
"securityDefinitions":
"security":
"@type":
"title":
"description":
"properties":
"actions":
}
"
Phi3-mini on edge: "Your task: Please create an appropriate WoT Thing Description for the TP-Link VIGI C240 camera. Ensure that it is a valid JSON format with all necessary fields filled and relevant to its functionality as per WOoTC specifications. Note, you do not need to include security definitions or details related to IoT protocols in your file here; these are assumed for later integration into the system's infrastructure setup if required by network administrators/security teams.
Output:```json
{
"@context": "http://schema.org",
"id": "#TP-LinkVIGIC240",
"description": {
"@type": "RDFaDescription",
"headline": "TP-Link VIGI C240 Full HD Dome Camera with Wireless Remote Control"
},
"name": "TP-LINK Vigilant X Series II: TP-Link VIGI C240 (1366x768)"
,
"@type": [
"Thing",
{
"@id": "#CAMER
"

The Limitation of local LLM is that it cannot generate a long context/too many fields as those in one entire WoT file. It has limited processing memory and will generate halfway and stop. One possible way is to let it generate key field by field by calling it multiple times. or generate the key content and we fill it into the WoT template programmatically.


