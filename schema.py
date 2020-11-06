import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, Department as DepartmentModel, Employee as EmployeeModel


class Department(SQLAlchemyObjectType):
    class Meta:
        model = DepartmentModel
        interfaces = (relay.Node, )


class Employee(SQLAlchemyObjectType):
    class Meta:
        model = EmployeeModel
        interfaces = (relay.Node, )

class SearchResult(graphene.Union):
    class Meta:
        types = (Department, Employee)


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    search = graphene.List(SearchResult, q=graphene.String())

    all_employees = SQLAlchemyConnectionField(Employee.connection)
    all_departments = SQLAlchemyConnectionField(
        Department.connection, sort=None)

    def resolve_search(self, info, **args):
        q = args.get("q")  # Search query

        # Get queries
        department_query = Department.get_query(info)
        employee_query = Employee.get_query(info)

        # Query Books
        books = department_query.filter((DepartmentModel.name.contains(q)) |
                                      (DepartmentModel.id.contains(q)) |
                                      (DepartmentModel.employees.any(EmployeeModel.name.contains(q)))).all()

        # Query Authors
        authors = employee_query.filter(EmployeeModel.name.contains(q)).all()

        return authors + books  # Com


schema = graphene.Schema(query=Query)
