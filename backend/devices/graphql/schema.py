import strawberry
from devices.graphql.mutations import Mutation as DeviceMutation
from devices.graphql.queries import Query as DeviceQuery
from gqlauth.user import arg_mutations as auth_mutations

@strawberry.type
class Mutation(DeviceMutation):
    # Auth mutations
    # TODO: test and implement JWT authentication logic
    register = auth_mutations.Register.field
    login = auth_mutations.ObtainJSONWebToken.field
    verify_token = auth_mutations.VerifyToken.field
    refresh_token = auth_mutations.RefreshToken.field
    logout = auth_mutations.RevokeToken.field
    update_account = auth_mutations.UpdateAccount.field

schema = strawberry.Schema(query=DeviceQuery, mutation=Mutation)
