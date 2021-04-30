import graphene

class TestMutation(graphene.Mutation):
  class Arguments:
    param = graphene.String()
  ok = graphene.Boolean()
  rstr = graphene.String()

  def mutate(root, info, param):
    ok = True
    return TestMutation(ok=ok, rstr=param)

class Query(graphene.ObjectType):
  HealthCheck = graphene.Boolean()

  def resolve_HealthCheck(root, info):
    return True

class Mutation(graphene.ObjectType):
  TestMutation = TestMutation.Field()

Schema = graphene.Schema(query=Query, mutation=Mutation)