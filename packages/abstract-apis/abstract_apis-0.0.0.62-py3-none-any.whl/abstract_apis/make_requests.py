import json
import requests
import aiohttp
from abstract_utilities import *
import asyncio

async def getAsyncRequest(url, data, headers):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=data, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()
async def postAsyncRequest(url, data, headers):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=data, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()                    
def get_headers():
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

def ensure_json(data):
    if isinstance(data, str):
        try:
            json.loads(data)  # Verify it's valid JSON
            return data
        except ValueError:
            pass  # Not valid JSON, continue to dump it
    return json.dumps(data)

def stripit(string, chars=[]):
    string = string or ''
    for char in make_list(chars):
        string = string.strip(char)
    return string

def make_endpoint(endpoint):
    return stripit(endpoint, chars='/')

def make_url(url):
    return stripit(url, chars='/')

def get_url(url, endpoint=None):
    return stripit(f"{make_url(url)}/{make_endpoint(endpoint)}", chars='/')

def get_text_response(response):
    try:
        return response.text
    except Exception as e:
        print(f"Could not read text response: {e}")
        return None

def load_inner_json(data):
    """Recursively load nested JSON strings within the main JSON response, even if nested within lists."""
    if isinstance(data, str):
        try:
            return load_inner_json(json.loads(data))  # Recursively parse inner JSON strings
        except (ValueError, TypeError):
            return data
    elif isinstance(data, dict):
        return {key: load_inner_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [load_inner_json(item) for item in data]
    return data

def get_json_response(response, response_result=None, load_nested_json=True):
    response_result = response_result or 'result'
    try:
        response_json = response.json()
        if isinstance(response_json,dict):
            response_json = response_json.get(response_result, response_json)
        if load_nested_json:
            response_json = load_inner_json(response_json)
        if response_json is not None:
            return response_json
        # Fallback to the last key if 'result' is not found
        last_key = list(response_json.keys())[-1] if response_json else None
        return response_json.get(last_key, None)
    except Exception as e:
        print(f"Could not read JSON response: {e}")
        return None
def async_json_response(response, response_result=None, load_nested_json=True):
    response_result = response_result or 'result'
    try:
        response_json = response.json()
        if isinstance(response_json,dict):
            response_json = response_json.get(response_result, response_json)
        if load_nested_json:
            response_json = load_inner_json(response_json)
        if response_json is not None:
            return response_json
        # Fallback to the last key if 'result' is not found
        last_key = list(response_json.keys())[-1] if response_json else None
        return response_json.get(last_key, None)
    except Exception as e:
        print(f"Could not read JSON response: {e}")
        return None

def get_status_code(response):
    try:
        return response.status_code
    except Exception as e:
        print(f"Could not get status code: {e}")
        return None

async def async_response(response, response_result=None, raw_response=False, load_nested_json=True):
    if raw_response:
        return response
    json_response = await async_json_response(response, response_result=response_result, load_nested_json=load_nested_json)
    if json_response is not None:
        return json_response
    text_response = get_text_response(response)
    if text_response:
        return text_response
    return response.content  # Return raw content as a last resort
def get_response(response, response_result=None, raw_response=False, load_nested_json=True):
    if raw_response:
        return response
    json_response = get_json_response(response, response_result=response_result, load_nested_json=load_nested_json)
    if json_response is not None:
        return json_response
    text_response = get_text_response(response)
    if text_response:
        return text_response
    return response.content  # Return raw content as a last resort

async def asyncMake_request(url, data=None, headers=None, method='GET', endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    url = get_url(url, endpoint=endpoint)
    if headers is None:
        headers = get_headers()
    data = ensure_json(data)

    try:
        if method.upper() == 'POST':
            response =  await postAsyncRequest(url, data=json.loads(data), headers=headers)
        elif method.upper() == 'GET':
            response = await getAsyncRequest(url, data=json.loads(data), headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    except Exception as e:
        print(f"Could not make {method} request: {e}")
        if status_code:
            return None, None
        return None

    if status_code:
        return await async_response(response, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json), get_status_code(response)
    return await async_response(response, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)
def make_request(url, data=None, headers=None, method='GET', endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    url = get_url(url, endpoint=endpoint)
    if headers is None:
        headers = get_headers()
    data = ensure_json(data)

    try:
        if method.upper() == 'POST':
            response = requests.post(url, params=data, headers=headers)
        elif method.upper() == 'GET':
            response = requests.get(url, params=data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    except Exception as e:
        print(f"Could not make {method} request: {e}")
        if status_code:
            return None, None
        return None

    if status_code:
        return get_response(response, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json), get_status_code(response)
    return get_response(response, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)

async def asyncPostRequest(url, data, headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    return await asyncMake_request(url, data=data, headers=headers, endpoint=endpoint, method='POST', status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)

async def asyncGetRequest(url, data, headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    return await asyncMake_request(url, data=data, headers=headers, endpoint=endpoint, method='GET', status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)
def postRequest(url, data, headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    return make_request(url, data=data, headers=headers, endpoint=endpoint, method='POST', status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)

def getRequest(url, data, headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    return make_request(url, data=data, headers=headers, endpoint=endpoint, method='GET', status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)
