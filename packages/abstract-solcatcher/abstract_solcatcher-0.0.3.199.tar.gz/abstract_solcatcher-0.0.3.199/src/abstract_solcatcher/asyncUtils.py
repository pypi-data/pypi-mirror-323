import asyncio,httpx,logging,json
from .utils import *
from abstract_apis import get_headers,get_response,get_async_response

def safe_json_dumps(obj):
    if isinstance(obj, dict):
        obj = json.dumps(obj)
    return obj

async def async_make_request(url, payload, headers=None):
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.post(url, data=safe_json_dumps(payload), headers=headers)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        return response  # or just return response if you want the full object

def get_kwargs_bools(key, bools, **kwargs):
    bools[key] = kwargs.get(key)
    if key in kwargs:
        del kwargs[key]
    return bools, kwargs

def get_solcatcherSettings(getApi=False, **kwargs):
    bools = {}
    
    bools, kwargs = get_kwargs_bools(key='solcatcherSettings', bools=bools, **kwargs)
    bools, kwargs = get_kwargs_bools(key='headers', bools=bools, **kwargs)
    headers = bools.get('headers', get_headers())
    bools, kwargs = get_kwargs_bools(key='solcatcherApiKey', bools=bools, **kwargs)
    apiKey = bools.get('apiKey')
    if apiKey or getApi:
        apiKey = apiKey or getApi
        if isinstance(apiKey, bool):
            apiKey = None
        headers = get_db_header(headers=headers, api_key=apiKey)
    headers = headers or get_headers()
    return kwargs, bools.get('solcatcherSettings'), headers, bools

def get_response_option(response, option='json'):
    """
    Get the response in the desired format: either JSON or Text.
    """
    if option == 'json':
        return response.json() if response.is_json else response.text
    elif option == 'text':
        return response.text
    else:
        raise ValueError("Option must be 'json' or 'text'")

def get_result_option(response, key='result'):
    """
    Retrieve a value based on the key from the response.
    If the key is not in the response, return the original response or a default.
    """
    if isinstance(response, dict):
        return response.get(key, response)  # Get value by key, else return the whole response
    return response

def runSolcatcherSettings(response, solcatcherSettings):
    usedKeys = []
    status_code = response.status_code
    if solcatcherSettings:
        if 'getResponse' in solcatcherSettings and solcatcherSettings.get('getResponse') != False:
            response = get_response(response)
            usedKeys.append('getResponse')
        if 'getResult' in solcatcherSettings:
            desired_result = solcatcherSettings.get('getResult')
            if desired_result in [True, None]:
                desired_result = 'result'
            if isinstance(response,dict):
                response = response.get(desired_result,response)
            usedKeys.append('getResult')
        if 'getStatusCode' in solcatcherSettings and solcatcherSettings.get('getStatusCode') != False:
            response = {"result": response, "status_code": status_code}
    return response
def process_settings(*args, **kwargs):
    kwargs["solcatcherSettings"] = kwargs.get("solcatcherSettings") or {"getResponse":True,"getResult":True}
    kwargs, solcatcherSettings, headers, bools = get_solcatcherSettings(**kwargs)
    payload = get_payload(*args, **kwargs)
    return kwargs, solcatcherSettings, headers, bools, payload
async def async_call_solcatcher_ts(endpoint, *args, **kwargs):
    kwargs, solcatcherSettings, headers, bools, payload = process_settings(*args, **kwargs)
    url = getSolcatcherTsUrl(endpoint=endpoint)
    response = await async_make_request(url, payload, headers=headers)
    result = runSolcatcherSettings(response, solcatcherSettings)
    return result

async def async_call_solcatcher_py(endpoint, *args, **kwargs):
    kwargs, solcatcherSettings, headers, bools, payload = process_settings(*args, **kwargs)
    url = getSolcatcherPairCatchUrl(endpoint=endpoint)
    response = await async_make_request(url, payload, headers=headers)
    result = runSolcatcherSettings(response, solcatcherSettings)
    return result

async def async_call_solcatcher_db(endpoint, *args, **kwargs):
    kwargs, solcatcherSettings, headers, bools, payload = process_settings(*args, **kwargs)
    url = getSolcatcherDbCalls(endpoint=endpoint)
    response = await async_make_request(url, payload, headers=headers)
    result = runSolcatcherSettings(response, solcatcherSettings)
    return result


async def async_call_rate_limiter(method, params=None, url_1_only=None, url_2_only=None,**kwargs):
    """
    A rate-limited caller that funnels into makeLimitedRpcCall.
    """
    params = params or []
    url_1_only = True if url_1_only is None else url_1_only
    url_2_only = False if url_2_only is None else url_2_only
    unique_item = params[0] if params else params
    try:
        logging.debug(f"Fetching transaction for signature={unique_item}")
        response = await makeLimitedRpcCall(method=method, params=params,
                                            url_1_only=url_1_only,
                                            url_2_only=url_2_only,
                                            **kwargs)
        logging.debug(f"Raw response from {method} for {unique_item}.")
        return response
    except Exception as e:
        logging.error(f"Error fetching {method}: {e}")
        return []

async def async_make_rate_limited_call(method, params, url_1_only=True, url_2_only=False,*args,**kwargs):
    """
    Attempt up to 3 times. After the 2nd attempt, set url_2_only=True.
    After the 1st attempt, set url_1_only=False.
    """
    ogsettings = kwargs.get('solcatcherSettings',{})
    solcatcherSettings={"getStatusCode":True}
    solcatcherSettings.update(ogsettings)
    kwargs['solcatcherSettings']=solcatcherSettings
    kwargs,solcatcherSettings,headers,bools = get_solcatcherSettings(**kwargs)
    for attempt in range(3):  # Retry logic
        if attempt == 2:
            url_2_only = True
        if attempt == 1:
            url_1_only = False
        
        result = await async_call_solcatcher_py(
            'make_limited_rpc_call',
            method=method,
            params=params,
            url_1_only=url_1_only,
            url_2_only=url_2_only,
            solcatcherSettings=solcatcherSettings,
            headers = headers,
            **kwargs
        )

        if solcatcherSettings.get('getStatusCode'):
            if isinstance(result,dict):
                status_code = result.get('status_code')
                results = result.get('result')
                if status_code and status_code != 429:
                    if ogsettings.get('getStatusCode'):
                        return result
                    else:
                        del result['status_code']
                    get_result = solcatcherSettings.get('getResult')
                    if 'getResult' in solcatcherSettings and get_result != False:
                        if get_result in [True,None]:
                            get_result = 'result'
                        result = result.get(get_result,result)
                    return result

        elif result:
            return result
    # If no response after all attempts, return empty or raise an exception
    return []
def make_request(url=None, payload={}, headers=None, url_1_only=None, url_2_only=False,*args, **kwargs):
    if url == None:
        if (url_1_only == None and url_2_only==None) or (url_1_only and not url_2_only):
            url = solana_rpc_url
        elif (not url_1_only and url_2_only) or (url_1_only and url_2_only):
            url = fall_back_rpc
    url = url or solana_rpc_url
    return get_async_response(async_make_reques,url=url,payload=payload,headers=headers or get_headers())
def call_rate_limiter(method, params, url_1_only=True, url_2_only=False,*args, **kwargs):
    return get_async_response(async_call_rate_limiter,method=method, params=params, url_1_only=url_1_only, url_2_only=url_2_only,*args, **kwargs)

def make_rate_limited_call(method, params, url_1_only=True, url_2_only=False,*args, **kwargs):
    return get_async_response(async_make_rate_limited_call(method=method, params=params, url_1_only=url_1_only, url_2_only=url_2_only,*args, **kwargs))

def call_solcatcher_py(endpoint, *args, **kwargs):
    return get_async_response(async_call_solcatcher_py,endpoint, *args, **kwargs)

def call_solcatcher_ts(endpoint, *args, **kwargs):
    return get_async_response(async_call_solcatcher_ts,endpoint, *args, **kwargs)

def call_solcatcher_db(endpoint, *args, **kwargs):
    return get_async_response(async_call_solcatcher_db,endpoint, *args, **kwargs)


