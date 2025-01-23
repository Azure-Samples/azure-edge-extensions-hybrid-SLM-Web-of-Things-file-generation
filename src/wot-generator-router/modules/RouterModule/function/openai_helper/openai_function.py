# import os
# from enum import Enum
# from openai import OpenAI
# from openai import AzureOpenAI
# from tenacity import retry, wait_random_exponential, stop_after_attempt  
# from function.openai_helper.config import *
  
# import json  
# import openai  
# from azure.core.credentials import AzureKeyCredential  
# # from azure.search.documents import SearchClient  
# # from azure.search.documents.indexes import SearchIndexClient  
# # from azure.search.documents.models import Vector  
# # from azure.search.documents.indexes.models import (  
# #     SearchIndex,  
# #     SearchField,  
# #     SearchFieldDataType,  
# #     SimpleField,  
# #     SearchableField,  
# #     SearchIndex,  
# #     SemanticConfiguration,  
# #     PrioritizedFields,  
# #     SemanticField,  
# #     SearchField,  
# #     SemanticSettings,  
# #     VectorSearch,  
# #     VectorSearchAlgorithmConfiguration,  
# # )  

# class AzureVectorSearch:
#     openai.api_type = API_TYPE
#     openai.api_key = AZURE_OPENAI_API_KEY
#     openai.api_base = AZURE_OPENAI_ENDPOINT
#     openai.api_version = AZURE_OPENAI_API_VERSION
    
#     def __init__(self):  
#         self.credential = AzureKeyCredential(AZURE_SEARCH_API_KEY)

#     def openAI_ChatCompletion(self, sys_meg, query):
#         # https://platform.openai.com/docs/guides/gpt/chat-completions-api
#         # retrieval = openai.ChatCompletion.create(engine=CHAT_MODEL,messages=[{'role':"user",'content': query}],max_tokens=500)
#         retrieval = openai.ChatCompletion.create(engine=CHAT_MODEL,messages=[{'role':"system",'content': sys_meg},{'role':"user",'content': query}], temperature=0)
#         # Response provided by GPT-3.5
#         return retrieval['choices'][0]['message']['content']

#     @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
#     # Function to generate embeddings for title and content fields, also used for query embeddings
#     def generate_embeddings(self, text):
#         response = openai.Embedding.create(
#             input=text, engine=EMBEDDING_MODEL)
#         embeddings = response['data'][0]['embedding']
#         return embeddings
        
#     def delete_search_index(self, index_name):
#         # Delete a search index
#         index_client = SearchIndexClient(
#             endpoint=AZURE_SEARCH_SERVICE_ENDPOINT, credential=self.credential)
#         result = index_client.delete_index(index_name)
#         return result

#     def create_search_index(self, index_name):
#         # Create a search index
#         index_client = SearchIndexClient(
#             endpoint=AZURE_SEARCH_SERVICE_ENDPOINT, credential=self.credential)

#         fields = [
#             SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
#             SearchableField(name="content", type=SearchFieldDataType.String),
#             SearchableField(name="product", type=SearchFieldDataType.String,filterable=True),
#             SearchableField(name="category", type=SearchFieldDataType.String,filterable=True),

#             SearchField(name="contentVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
#                         searchable=True, vector_search_dimensions=1536, vector_search_configuration="my-vector-config"),
#         ]

#         vector_search = VectorSearch(
#             algorithm_configurations=[
#                 VectorSearchAlgorithmConfiguration(
#                     name="my-vector-config",
#                     kind="hnsw",
#                     hnsw_parameters={
#                         "m": 4,
#                         "efConstruction": 400,
#                         "efSearch": 500,
#                         "metric": "cosine"
#                     }
#                 )
#             ]
#         )

#         semantic_config = SemanticConfiguration(
#             name="my-semantic-config",
#             prioritized_fields=PrioritizedFields(
#                 title_field=SemanticField(field_name="product"),
#                 prioritized_keywords_fields=[SemanticField(field_name="category")],
#                 prioritized_content_fields=[SemanticField(field_name="content")]
#             )
#         )

#         # Create the semantic settings with the configuration
#         semantic_settings = SemanticSettings(configurations=[semantic_config])

#         # Create the search index with the semantic settings
#         index = SearchIndex(name=index_name, fields=fields,
#                             vector_search=vector_search, semantic_settings=semantic_settings)
#         result = index_client.create_or_update_index(index)
#         return result


#     def list_index_names(self):
#         index_client = SearchIndexClient(endpoint=AZURE_SEARCH_SERVICE_ENDPOINT, credential=self.credential)
#         index_names = index_client.list_index_names()
#         return index_names

#     def upload_documents(self, index_name, documents):
#         search_client = SearchClient(endpoint=AZURE_SEARCH_SERVICE_ENDPOINT, index_name=index_name, credential=self.credential)
#         result = search_client.upload_documents(documents)
#         return result
    
#     # vectorizer is defined. this is query using indexer. vector fields include vectorizer and its profile, and search config
#     def vector_similarity_search(self, index_name, vector_fields, search_text):
#         search_client = SearchClient(AZURE_SEARCH_SERVICE_ENDPOINT, index_name, credential=self.credential)  
#         results = search_client.search(  
#             search_text=None,  
#             vector=self.generate_embeddings(search_text),
#             top_k=5,
#             vector_fields=vector_fields,
#             select=["product", "category", "content"],
#         )

#         # for result in results:  
#         #     print(f"cn: {result['cn']}")  
#         #     print(f"en: {result['en']}")  
#         #     print(f"Score: {result['@search.score']}")  
#         #     print(f"updateby: {result['updateby']}")  
#         #     print(f"customer: {result['customer']}")  
#         #     print(f"Category: {result['category']}\n")  

#         return results