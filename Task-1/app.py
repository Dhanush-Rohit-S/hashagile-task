import pandas as pd
import uuid
from neo4j import GraphDatabase

# Neo4j connection details
uri = "" # Replace with your actual URI
username = ""  # Replace with your actual username
password = ""  # Replace with your actual password

driver = GraphDatabase.driver(uri, auth=(username, password))

def create_graph(tx, candidate_id, candidate, email, college, year_of_passout, degree, skills):
    tx.run("""
    MERGE (c:Candidate {id: $candidate_id, name: $name, email: $email, year_of_passout: $year_of_passout})
    """, candidate_id=candidate_id, name=candidate, email=email, year_of_passout=year_of_passout)

    tx.run("""
    MERGE (cl:College {name: $college})
    MERGE (c:Candidate {id: $candidate_id})
    MERGE (c)-[:STUDIED_AT]->(cl)
    """, candidate_id=candidate_id, college=college)

    tx.run("""
    MERGE (d:Degree {name: $degree})
    MERGE (c:Candidate {id: $candidate_id})
    MERGE (c)-[:HAS_DEGREE]->(d)
    """, candidate_id=candidate_id, degree=degree)

    for skill in skills:
        tx.run("""
        MERGE (s:Skill {name: $skill})
        MERGE (c:Candidate {id: $candidate_id})
        MERGE (c)-[:HAS_SKILL]->(s)
        """, candidate_id=candidate_id, skill=skill.strip())

def process_candidates(session, df):
    for index, row in df.iterrows():
        candidate_id = str(uuid.uuid4())  # Generate a unique ID for each candidate
        candidate = row['Name']
        email = row['Email']
        college = row['College']
        year_of_passout = row['Year of Passout']
        degree = row['Degree']
        skills = row['Skills'].split(',')

        # Add data to the Neo4j graph
        session.write_transaction(create_graph, candidate_id, candidate, email, college, year_of_passout, degree, skills)

def main():
    # Reading the data from the CSV file
    df = pd.read_csv('data.csv')

    # Start Neo4j session and write data
    with driver.session() as session:
        process_candidates(session, df)


if __name__ == "__main__":
    main()
