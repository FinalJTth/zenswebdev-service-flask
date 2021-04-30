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