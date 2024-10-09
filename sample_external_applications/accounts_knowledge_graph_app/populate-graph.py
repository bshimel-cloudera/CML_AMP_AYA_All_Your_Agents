import os
import sys
from langchain_community.graphs import Neo4jGraph
import json
import time 
import random

import sys

from sample_external_applications.accounts_knowledge_graph_app.neo4j_utils import (
    get_neo4j_credentails,
)

def create_or_update_account(graph, account):
    # Merge the Account node
    query = """
        MERGE (a:Account {name: $name})
        SET a.industry = $industry,
            a.total_employees = $total_employees
    """
    params = {
        "name": account.get("name", ""),
        "industry": account.get("industry", ""),
        "total_employees": account.get("total_employees", 0),
    }
    graph.query(query, params=params)

def create_or_update_employee(graph, employee_data):
    # Merge the Employee node based on email
    query = """
        MERGE (e:Employee {email: $email})
        SET e.first_name = $first_name,
            e.last_name = $last_name
    """
    params = {
        "email": employee_data["email"],
        "first_name": employee_data.get("first_name", ""),
        "last_name": employee_data.get("last_name", "")
    }
    graph.query(query, params=params)

def create_or_update_role(graph, role_name):
    # Merge the Role node
    query = """
        MERGE (r:Role {name: $role_name})
    """
    params = {
        "role_name": role_name
    }
    graph.query(query, params=params)

def create_person_role_relationship(graph, email, role_name):
    # Create relationship between Person and Role
    query = """
        MATCH (e:Employee {email: $email})
        MATCH (r:Role {name: $role_name})
        MERGE (e)-[:HOLDS_ROLE]->(r)
    """
    params = {
        "email": email,
        "role_name": role_name
    }
    graph.query(query, params=params)

def create_account_employee_relationship(graph, account_name, employee_email):
    # Create relationship between Person and Account
    query = """
        MATCH (a:Account {name: $account_name})
        MATCH (e:Employee {email: $email})
        MERGE (e)-[:EMPLOYED_AT]->(a)
    """
    params = {
        "account_name": account_name,
        "email": employee_email
    }
    graph.query(query, params=params)

def create_or_update_product(graph, product_data):
    # Merge the Product node
    query = """
        MERGE (p:Product {name: $product_name})
        SET p.requires_gpu = $requires_gpu
    """
    params = {
        "product_name": product_data["name"],
        "requires_gpu": product_data["requires_gpu"]
    }
    graph.query(query, params=params)

def create_account_product_relationship(graph, account_name, product_name):
    # Create relationship between product and Product
    query = """
        MATCH (a:Account {name: $account_name})
        MATCH (p:Product {name: $product_name})
        MERGE (a)-[:OWNS_PRODUCT]->(p)
    """
    params = {
        "account_name": account_name,
        "product_name": product_name
    }
    graph.query(query, params=params)


def clear_graph(graph: Neo4jGraph):
    graph.query("MATCH (n) DETACH DELETE n")
    return


def populate_database(graph: Neo4jGraph):
    kg_data = json.load(open("sample_external_applications/accounts_knowledge_graph_app/kg_data.json"))
    
    # Clear the graph.
    print("Clearing the graph...")
    clear_graph(graph)

    # Add data
    print("Beginning population...")
    t0 = time.time()
    for ii, account in enumerate(kg_data["accounts"]):
        print(f"{ii}: {account['name']}")
        create_or_update_account(graph, account)
        for employee in account.get("employees", []):
            create_or_update_employee(graph, employee)
            create_or_update_role(graph, employee["role"])
            create_person_role_relationship(graph, employee["email"], employee["role"])
            create_account_employee_relationship(graph, account["name"], employee["email"])
        for product in account.get("products", []):
            print(f"  - account '{account['name']}' has product '{product['name']}'.")
            create_or_update_product(graph, product)
            create_account_product_relationship(graph, account["name"], product["name"]) 
        for person in account.get("support_team", []):
            create_or_update_employee(graph, person)
            create_or_update_role(graph, person["role"])
            create_person_role_relationship(graph, person["email"], person["role"])
            create_account_employee_relationship(graph, "Cloudera", person["email"])
    print("Graph indexing complete!")
    return


def main():

    # Get the graph client
    graph = Neo4jGraph(
        username=get_neo4j_credentails()["username"],
        password=get_neo4j_credentails()["password"],
        url=get_neo4j_credentails()["uri"],
    )

    populate_database(graph)
    
    return



if __name__ == "__main__":
    main()
