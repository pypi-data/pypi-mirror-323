from .request_utils import *
async def getAsyncRequest(url, data=None, headers=None,,endpoint=None):
    async with aiohttp.ClientSession() as session:
        values = get_values_js(url=url,data=data,headers=headers,endpoint=endpoint)
        async with session.get(**values) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()
async def postAsyncRequest(url, data=None, headers=None,endpoint=None):
    async with aiohttp.ClientSession() as session:
        values = get_values_js(url=url,data=data,headers=headers,endpoint=endpoint)
        async with session.post(**values) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()                    

async def asyncMakeRequest(url, data=None, headers=None, get_post=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    response = None
    get_post = get_post.upper() or ('GET' if data == None else 'POST')
    if get_post == 'POST':
        response = await postAsyncRequest(url, data=data, headers=headers,endpoint=endpoint)
    elif get_post == 'GET':
        response = await getAsyncRequest(url, data=data, headers=headers,endpoint=endpoint)
    else:
        raise ValueError(f"Unsupported HTTP get_post: {get_post}")


    if status_code:
        return get_response(response, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json), get_status_code(response)
    return get_response(response, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)


async def asyncPostRequest(url, data, headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    return await asyncMakeRequest(url, data=data, headers=headers, endpoint=endpoint, get_post='POST', status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)

async def asyncGetRequest(url, data, headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    return await asyncMakeRequest(url, data=data, headers=headers, endpoint=endpoint, get_post='GET', status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)

async def getRpcRequest(url, method=None,params=None,jsonrpc=None,id=None,headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    data = getRpcData(method=method,params=params,jsonrpc=jsonrpc,id=id)
    return await getRequest(url, data, headers=headers, endpoint=endpoint, status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)

async def postRpcRequest(url, method=None,params=None,jsonrpc=None,id=None,headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    data = getRpcData(method=method,params=params,jsonrpc=jsonrpc,id=id)
    return await asyncPostRequest(url, data, headers=headers, endpoint=endpoint, status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)
