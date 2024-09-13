import streamlit as st
import subprocess
import json
import boto3
from bs4 import BeautifulSoup
import requests

# Function to run Lighthouse for performance metrics
def run_lighthouse(url):
    try:
        # Full path to npx and output file
        npx_path = r'C:\Users\spokhrel\AppData\Roaming\npm\npx.cmd'
        output_path = 'lighthouse-report.json'
        
        # Run Lighthouse command
        result = subprocess.run([
            npx_path, 'lighthouse', url, '--output', 'json', '--output-path', output_path,
            '--chrome-flags="--headless --disable-gpu"'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

        if result.returncode != 0:
            st.error(f"Lighthouse Error: {result.stderr}")
            return None

        # Load the Lighthouse JSON result
        with open(output_path, 'r', encoding='utf-8') as f:
            lighthouse_result = json.load(f)

        return lighthouse_result
    except Exception as e:
        st.error(f"Error running Lighthouse: {str(e)}")
        return None

# Function to perform basic SEO checks
def seo_check(url):
    try:
        session = requests.Session()
        response = session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Basic SEO metrics
        title = soup.find('title').text if soup.find('title') else 'No title found'
        meta_desc = soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else 'No meta description found'
        h1 = soup.find('h1').text if soup.find('h1') else 'No H1 tag found'

        return {
            "title": title,
            "meta_description": meta_desc,
            "h1": h1
        }
    except Exception as e:
        st.error(f"Error fetching SEO data: {str(e)}")
        return None

# Function to call AWS Bedrock for GenAI suggestions




import json
import boto3

import json
import boto3

import json
import boto3

def get_genai_suggestions(performance_data, seo_data):
    try:
        client = boto3.client('bedrock-runtime')

        # Construct the prompt with performance and SEO data
        prompt = (
            "Human: Analyze the following website performance and SEO data and provide suggestions for improvement.\n\n"
            f"Performance Data:\n"
            f"Mobile Performance Score: {performance_data.get('categories', {}).get('performance', {}).get('score', 0) * 100}\n"
            f"Mobile LCP: {performance_data.get('audits', {}).get('largest-contentful-paint', {}).get('displayValue', 'N/A')}\n"
            f"Mobile FCP: {performance_data.get('audits', {}).get('first-contentful-paint', {}).get('displayValue', 'N/A')}\n"
            f"Mobile TTFB: {performance_data.get('audits', {}).get('time-to-first-byte', {}).get('displayValue', 'N/A')}\n"
            f"Mobile First Interactive: {performance_data.get('audits', {}).get('interactive', {}).get('displayValue', 'N/A')}\n"
            f"Desktop Performance Score: {performance_data.get('categories', {}).get('performance', {}).get('score', 0) * 100}\n"
            f"Desktop LCP: {performance_data.get('audits', {}).get('largest-contentful-paint', {}).get('displayValue', 'N/A')}\n"
            f"Desktop FCP: {performance_data.get('audits', {}).get('first-contentful-paint', {}).get('displayValue', 'N/A')}\n"
            f"Desktop TTFB: {performance_data.get('audits', {}).get('time-to-first-byte', {}).get('displayValue', 'N/A')}\n"
            f"Desktop First Interactive: {performance_data.get('audits', {}).get('interactive', {}).get('displayValue', 'N/A')}\n\n"
            f"SEO Data:\n"
            f"Title: {seo_data.get('title', 'N/A')}\n"
            f"Meta Description: {seo_data.get('meta_description', 'N/A')}\n"
            f"H1: {seo_data.get('h1', 'N/A')}\n\n"
            "Human: Provide specific suggestions to improve the website's performance and SEO based on the above data.\n\n"
            "Assistant:"
        )

        # Create the request payload according to the Bedrock API format
        payload = {
            "modelId": "anthropic.claude-v2:1",
            "contentType": "application/json",
            "accept": "*/*",
            "body": json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 300,
                "temperature": 0.5,
                "top_k": 250,
                "top_p": 1,
                "stop_sequences": ["\n\nHuman:"],
                "anthropic_version": "bedrock-2023-05-31"
            })
        }

        # Make the request to AWS Bedrock
        response = client.invoke_model(**payload)

        # Read the StreamingBody content
        response_body = response['body'].read().decode('utf-8')

        # Log the response body for debugging
        print(f"Response Body: {response_body}")

        # Parse the response body
        parsed_response = json.loads(response_body)
        return parsed_response.get('choices', [{}])[0].get('text', 'No suggestions returned')
    
    except Exception as e:
        print(f"Error calling AWS Bedrock: {str(e)}")
        return "No suggestions available due to an error."


def get_follow_up_answer(question):
    try:
        client = boto3.client('bedrock-runtime')

        # Create a detailed prompt for the LLM based on the follow-up question
        prompt = (
            f"Based on the previous suggestions and the provided website performance and SEO data, answer the following question:\n\n"
            f"Question: {question}\n\n"
            f"Provide a detailed response and, if applicable, actionable steps for improvement."
        )

        # Make the request to AWS Bedrock
        response = client.invoke_model(
            modelId="anthropic.claude-v2:1",
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 500,
                "temperature": 0.7
            }).encode('utf-8'),
            contentType="application/json",
            accept="*/*"
        )

        # Read the response body
        response_body = response['Body'].read().decode('utf-8')
        print(f"Raw Response Body: {response_body}")  # Log the raw response

        # Check if the response is empty
        if not response_body:
            print("Empty response body.")
            return "No response from the model."

        # Parse the response body
        parsed_response = json.loads(response_body)
        print(f"Parsed Response Body: {parsed_response}")  # Log the parsed response

        # Extract and return the text from the model's response
        answer = parsed_response.get('choices', [{}])[0].get('text', 'No answer returned')
        print(f"Model Answer: {answer}")
        return answer
    
    except Exception as e:
        print(f"Error calling AWS Bedrock: {str(e)}")
        return "No answer available due to an error."




# Function to calculate performance and SEO scores
def calculate_scores(lighthouse_data):
    try:
        # Extracting core metrics for scoring
        mobile_performance_score = lighthouse_data.get('categories', {}).get('performance', {}).get('score', 0) * 100
        desktop_performance_score = lighthouse_data.get('categories', {}).get('performance', {}).get('score', 0) * 100
        mobile_lcp = lighthouse_data.get('audits', {}).get('largest-contentful-paint', {}).get('displayValue', 'N/A')
        desktop_lcp = lighthouse_data.get('audits', {}).get('largest-contentful-paint', {}).get('displayValue', 'N/A')
        mobile_fcp = lighthouse_data.get('audits', {}).get('first-contentful-paint', {}).get('displayValue', 'N/A')
        desktop_fcp = lighthouse_data.get('audits', {}).get('first-contentful-paint', {}).get('displayValue', 'N/A')
        mobile_ttfb = lighthouse_data.get('audits', {}).get('time-to-first-byte', {}).get('displayValue', 'N/A')
        desktop_ttfb = lighthouse_data.get('audits', {}).get('time-to-first-byte', {}).get('displayValue', 'N/A')
        mobile_first_interactive = lighthouse_data.get('audits', {}).get('interactive', {}).get('displayValue', 'N/A')
        desktop_first_interactive = lighthouse_data.get('audits', {}).get('interactive', {}).get('displayValue', 'N/A')

        return {
            "mobile_performance_score": mobile_performance_score,
            "desktop_performance_score": desktop_performance_score,
            "mobile_lcp": mobile_lcp,
            "desktop_lcp": desktop_lcp,
            "mobile_fcp": mobile_fcp,
            "desktop_fcp": desktop_fcp,
            "mobile_ttfb": mobile_ttfb,
            "desktop_ttfb": desktop_ttfb,
            "mobile_first_interactive": mobile_first_interactive,
            "desktop_first_interactive": desktop_first_interactive
        }
    except Exception as e:
        st.error(f"Error calculating scores: {str(e)}")
        return None

# Streamlit UI
def analyze_assets(url):
    try:
        session = requests.Session()
        response = session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract CSS and JS file URLs
        css_files = [link['href'] for link in soup.find_all('link', rel='stylesheet') if link.has_attr('href')]
        js_files = [script['src'] for script in soup.find_all('script') if script.has_attr('src')]

        # This is a placeholder; in a real scenario, you'd analyze these files further
        # For now, just return the list of files found
        return {
            "css_files": css_files,
            "js_files": js_files
        }
    except Exception as e:
        st.error(f"Error analyzing assets: {str(e)}")
        return None

# Streamlit UI
st.title("Website Performance & SEO Checker with GenAI Suggestions")

url = st.text_input("Enter Website URL", value="https://www.example.com")

if st.button("Analyze"):
    with st.spinner('Analyzing the website...'):
        # Run Lighthouse to get performance data
        performance_data = run_lighthouse(url)
        
        if performance_data:
            # Fetch basic SEO data
            seo_data = seo_check(url)
            if seo_data:
                # Get AI-based suggestions from AWS Bedrock
                genai_suggestions = get_genai_suggestions(performance_data, seo_data)

                # Calculate performance and SEO scores
                scores = calculate_scores(performance_data)
                if scores:
                    st.subheader("Performance & SEO Scores")
                    st.write(scores)

                st.subheader("GenAI Suggestions")
                st.write(genai_suggestions)

                # Analyze assets
                assets = analyze_assets(url)
                if assets:
                    st.subheader("CSS and JS Files")
                    st.write(assets)

                # Follow-up question functionality
                follow_up_question = st.text_input("Ask a follow-up question")
                if st.button("Get Answer"):
                    answer = get_follow_up_answer(follow_up_question)
                    st.subheader("Follow-Up Answer")
                    st.write(answer)
            else:
                st.error("Error fetching SEO data.")
        else:
            st.error("Error running Lighthouse.")