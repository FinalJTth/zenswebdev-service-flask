import graphene
import requests
from utils.buildgql import buildgql

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

class Query(graphene.ObjectType):
  HealthCheck = graphene.Boolean(required=True)
  ValidateUsername = graphene.Field(ValidateObject, username=graphene.String(required=True))
  ValidateEmail = graphene.Field(ValidateObject, email=graphene.String(required=True))
  ValidatePassword = graphene.Field(ValidateObject, password=graphene.String(required=True))
  
  def resolve_HealthCheck(root, info):
    return True

  def resolve_ValidateUsername(root, info, username):
    if (r'^[a-zA-Z]', username) is not None:
      return ValidateObject(True, 'Username must start with a letter')
    if (r'^[a-zA-Z0-9]{0,}', username) is not None:
      return ValidateObject(True, 'Username contains implicit characters')
    if (r'^[a-zA-Z0-9]{8,30}', username) is not None:
      return ValidateObject(True, 'Username must be between 8 - 30 characters')
    quert = buildgql('query', 'User', { 'username': username }, ['username'])
    res = requests.post('https://localhost:9000/graphql', json={ query: query }, verify=False)
    if (res.status_code == 200):
      if (len(res.json()['data']['query']) > 0):
        return ValidateObject(True, 'Username has already been registered')
    else:
      return ValidateObject(True, 'Something went wrong while trying to check for existed user')
    return ValidateObject(False, 'Username is valid')
  
  def resolve_ValidateEmail(root, info, email):
    if (r'^[a-zA-Z0-9-._]$', email) is not None:
      return ValidateObject(True, 'Email contains implicit characters')
    if (r'^[a-zA-Z0-9-._]+@$', email) is not None:
      return ValidateObject(True, 'Missing @ character')
    if (r'^[a-zA-Z0-9-._]+@([a-zA-Z])$', email) is not None:
      return ValidateObject(True, 'Character @ must follow by proper domain name')
    if (r'^[a-zA-Z0-9-._]+@([a-zA-Z])+[.]{1,1}$', email) is not None:
      return ValidateObject(True, 'Missing . character')
    if (r'^[a-zA-Z0-9-._]+@([a-zA-Z])+[.]{1,1}([a-zA-Z]){2,4}$', email) is not None:
      return ValidateObject(True, 'Invalid domain extention')
    quert = buildgql('query', 'User', { 'email': email }, ['email'])
    res = requests.post('https://localhost:9000/graphql', json={ query: query }, verify=False)
    if (res.status_code == 200):
      if (len(res.json()['data']['query']) > 0):
        return ValidateObject(True, 'Email has already been registered')
    else:
      return ValidateObject(True, 'Something went wrong while trying to check for existed email')
    return ValidateObject(False, 'Email is valid')

  def resolve_ValidatePassword(root, info, password):
    if (r'^[A-Za-z0-9!"#$%&\'()*+,-./:;<>=?@[]{}\^_`~]+$', password) is not None:
      return ValidateObject(True, 'Password contains implicit characters')
    if (r'^(?=.*[A-Z]).+$', password) is not None:
      return ValidateObject(True, 'Password must contains at least one upper case')
    if (r'^(?=.*[0-9]).+$', password) is not None:
      return ValidateObject(True, 'Password must contains at least one number')
    if (r'^[A-Za-z0-9!"#$%&\'()*+,-./:;<>=?@[]{}\^_`~]{8,30}+$', password) is not None:
      return ValidateObject(True, 'Password must be between 8 - 30 characters')
    return ValidateObject(False, 'Password is valid')
class Mutation(graphene.ObjectType):
  TestMutation = TestMutation.Field()

Schema = graphene.Schema(query=Query, mutation=Mutation)