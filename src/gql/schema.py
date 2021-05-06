import graphene
from graphql import GraphQLSchema

from utils.requestsSession import backend
from utils.buildgql import buildgql

import json
import re
import base64
import warnings

from io import BytesIO
from PIL import Image

import numpy as np
from keras.preprocessing import image
from keras.applications import inception_v3

import requests

class TestMutation(graphene.Mutation):
  class Arguments:
    param = graphene.String(required=True)
  ok = graphene.Boolean()
  rstr = graphene.String()

  def mutate(root, info, param):
    ok = True
    return TestMutation(ok=ok, rstr=param)

class ValidateObject(graphene.ObjectType):
  isInvalid = graphene.Boolean(required=True)
  message = graphene.String()

class ClassifyReturnType(graphene.ObjectType):
  id = graphene.String()
  object = graphene.String()
  confident = graphene.Float()

class ClassifyObject(graphene.ObjectType):
  predictions = graphene.List(ClassifyReturnType)

class Query(graphene.ObjectType):
  HealthCheck = graphene.Boolean(required=True)
  ValidateUsername = graphene.Field(ValidateObject, username=graphene.String(required=True))
  ValidateEmail = graphene.Field(ValidateObject, email=graphene.String(required=True))
  ValidatePassword = graphene.Field(ValidateObject, password=graphene.String(required=True))

  ClassifyImage = graphene.Field(ClassifyObject, inputImage=graphene.String(required=True))
  
  def resolve_HealthCheck(root, info):
    return True

  def resolve_ValidateUsername(root, info, username):
    if (re.match(r'^[a-zA-Z]', username)) is None:
      return ValidateObject(True, 'Username must start with a letter')
    if (re.match(r'^[a-zA-Z0-9]{0,}$', username)) is None:
      return ValidateObject(True, 'Username contains implicit characters')
    if (re.match(r'^[a-zA-Z0-9]{8,30}$', username)) is None:
      return ValidateObject(True, 'Username must be between 8 - 30 characters')
    query = buildgql('query', 'User', { 'username': username }, ['username'])
    res = backend.post('/graphql', json={ 'query': query })
    if (res.status_code == 200):
      if (len(res.json()['data']['query']) > 0):
        return ValidateObject(True, 'Username has already been registered')
    else:
      return ValidateObject(True, 'Something went wrong while checking for existed user')
    return ValidateObject(False, 'Username is valid')
  
  def resolve_ValidateEmail(root, info, email):
    if (re.match(r'^[a-zA-Z0-9-._]', email)) is None:
      return ValidateObject(True, 'Email contains implicit characters')
    if (re.match(r'^[a-zA-Z0-9-._]+@', email)) is None:
      return ValidateObject(True, 'Missing @ character')
    if (re.match(r'^[a-zA-Z0-9-._]+@([a-zA-Z])', email)) is None:
      return ValidateObject(True, 'Character @ must follow by proper domain name')
    if (re.match(r'^[a-zA-Z0-9-._]+@([a-zA-Z])+[.]{1,1}', email)) is None:
      return ValidateObject(True, 'Missing . character')
    if (re.match(r'^[a-zA-Z0-9-._]+@([a-zA-Z])+[.]{1,1}([a-zA-Z]){2,4}$', email)) is None:
      return ValidateObject(True, 'Invalid domain extention')
    query = buildgql('query', 'User', { 'email': email }, ['email'])
    res = backend.post('/graphql', json={ 'query': query })
    if (res.status_code == 200):
      if (len(res.json()['data']['query']) > 0):
        return ValidateObject(True, 'Email has already been registered')
    else:
      return ValidateObject(True, 'Something went wrong while chercking for existed email')
    return ValidateObject(False, 'Email is valid')

  def resolve_ValidatePassword(root, info, password):
    if (re.match(r'^[A-Za-z0-9!"#$%&\'()*+,-./:;<>=?@\[\]{}\\\^_`~]', password)) is None:
      return ValidateObject(True, 'Password contains implicit characters')
    if (re.match(r'^(?=.*[A-Z]).+$', password)) is None:
      return ValidateObject(True, 'Password must contains at least one upper case')
    if (re.match(r'^(?=.*[0-9]).+$', password)) is None:
      return ValidateObject(True, 'Password must contains at least one number')
    if (re.match(r'[A-Za-z0-9!"#$%&\'()*+,-./:;<>=?@\[\]{}\\\^_`~]{8,30}$', password)) is None:
      return ValidateObject(True, 'Password must be between 8 - 30 characters')
    return ValidateObject(False, 'Password is valid')

  def resolve_ClassifyImage(root, info, inputImage):
    img_byte_filtered = re.sub('^data:image/.+;base64,|data: image/.+;base64 ', '', inputImage)
    img = Image.open(BytesIO(base64.b64decode(img_byte_filtered)))
    img = img.convert('RGB')
    img = img.resize((224, 224))
    img = image.img_to_array(img) / 255
    img = img.astype('float16')

    payload = {
      'instances': [img.tolist()]
    }

    r = requests.post('http://localhost:10000/v1/models/ImageClassifier:predict', json=payload)
    pred = json.loads(r.content.decode('utf-8'))
    pred_res = inception_v3.decode_predictions(np.array(pred['predictions']))[0]

    print(json.dumps(pred_res))

    predictions = []
    for result in pred_res:
      result_dict = {}
      result_dict['id'] = result[0]
      result_dict['object'] = result[1]
      result_dict['confident'] = result[2]
      predictions.append(result_dict)
    predictions = { 'predictions' : predictions }
    return predictions

class Mutation(graphene.ObjectType):
  TestMutation = TestMutation.Field()

Schema = graphene.Schema(query=Query, mutation=Mutation)
#assert isinstance(Schema.graphql_schema, GraphQLSchema)