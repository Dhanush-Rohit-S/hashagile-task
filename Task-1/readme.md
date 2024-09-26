# Candidate Data Import to Neo4j

This Python script imports candidate data from a CSV file into a Neo4j graph database. Each candidate is associated with nodes for their college, degree, and skills, and relationships are created between them.

## Features

- Reads candidate data from a CSV file.
- Automatically generates unique UUIDs for each candidate.
- Creates nodes for candidates, colleges, degrees, and skills.
- Creates relationships between candidates and their respective college, degree, and skills.
- Uses Neo4j as the graph database backend.

## Prerequisites

Ensure you have the following installed:

- Python 3.8+
- Pandas
- Neo4j Python Driver

You can install the required Python libraries using pip:

```bash
pip install pandas neo4j
```
