# Resume Parsing and Graph Storage App

This is a Flask web application that allows users to upload resumes in PDF format. The application extracts specific information from the resume, such as the candidate's name, email, college, degree, and skills using Google Generative AI (Gemini API), and stores this information in a Neo4j graph database.

## Features

- Upload a resume in PDF format.
- Extract candidate details (Name, Email, College, Year of Passout, Degree, and Skills) using Google Generative AI.
- Store candidate details in a Neo4j database.
- Visualize relationships such as `STUDIED_AT` (between Candidate and College) and `HAS_DEGREE`, `HAS_SKILL` (between Candidate and Degree/Skills).
- Fetch and display candidate details by email.

## Installation

```bash
pip install Flask neo4j google-generativeai werkzeug
```
