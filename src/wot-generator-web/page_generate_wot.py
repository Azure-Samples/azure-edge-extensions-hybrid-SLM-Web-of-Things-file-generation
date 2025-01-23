import streamlit as st
import time
import logging
import requests

#logging.basicConfig(level=logging.INFO)

def publish_user_input(user_input_json):
    backend_url = 'http://rag-router-service:8702/webpublish'
    try:
        logging.info('backend_url: ' + backend_url)
        logging.info('user_input_json: ' + user_input_json)
        response = requests.post(backend_url, json=user_input_json)
        if response.status_code == 200:
            category = response.json()['category']
            llm_to_use = response.json()['llm_to_use']
            st.success(f"Category: {category}, LLM in use: {llm_to_use}")
            st.success('User input published successfully')
        else:
            st.error('Failed to publish user input to the backend')
    except requests.RequestException as e:
        st.error(f'Request failed: {e}')

def query_retrieval():
    st.title('Please input your question:')
    # Search with manual selected LLM or auto selected by llm-router
    prompt = st.text_input('please input your question')
    llm_name = st.selectbox('Please select a LLM model you want to use',['auto select with llm-router','edge-phi3-mini', 'gpt-3.5-turbo'])
    if st.button('Submit'):
        if prompt:
            with st.spinner(text="Query Submitting..."):
                st.info('You selected LLM: {}'.format(llm_name))
                if llm_name == 'edge-phi3-mini':
                    selected_llm = 'edge-phi3-mini'
                elif llm_name == 'gpt-3.5-turbo':
                    selected_llm = 'gpt-3.5-turbo'
                else:
                    selected_llm = 'auto select with llm-router'
                user_input_json = {'user_query': prompt, 'selected_llm': selected_llm}
                publish_user_input(user_input_json)
        else:
            st.warning('Please input your question and select a LLM model to search')


if __name__ == "__main__":
    query_retrieval()
 
