import graphene
import contacts.schema
import sites.schema


class Query(sites.schema.Query, contacts.schema.Query, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

schema = graphene.Schema(query=Query)