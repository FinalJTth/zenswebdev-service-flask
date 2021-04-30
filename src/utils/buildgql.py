import requests
import json

def toGqlParamString(obj):
  param = ''
  for key, value in obj.items():
    param += f'{key}: "{value}" '
  return param[:-1]

def toGqlReturnValueString(arr):
  rval = '{'
  for value in arr:
    rval += f'{value} '
  return f'{rval[:-1]}}}'

def buildgql(type, resolver, parameter, returnValue=''):
  param = toGqlParamString(parameter)
  rval = f' {toGqlReturnValueString(returnValue)} ' if len(returnValue) > 0 else ''
  return f'{{ {type}: {resolver}({param}){rval}}}'

print(buildgql('query', 'ValidateUsername', { 'username': 'test' }, [ 'isValid', 'message' ]))
login = buildgql('query', 'Login', { 'username': 'test', 'password': '1234' })
res = requests.post('https://localhost:9000/graphql', json={ 'query': login })
print(json.dumps(res.json()))

#proxies={'https': 'http://127.0.0.1:9000/graphql'}