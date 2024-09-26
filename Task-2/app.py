import google.generativeai as genai
from neo4j import GraphDatabase
import uuid
import re
import json
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

# Replace the API key with your own Gemini API key
genai.configure(api_key='YOUR_GEMINI_API_KEY')

# Replace the URI with your Neo4j URI
uri = "YOUR_NEO4J_URI"
username = "YOUR_NEO4J_USERNAME"  # Replace with your actual username
password = "YOUR_NEO4J_PASSWORD"  # Replace with your actual password

driver = GraphDatabase.driver(uri, auth=(username, password))

# Extract JSON from the text response using regex
def extract_json(text_response):
    pattern = r'\{[^{}]*\}'  # Pattern to match simple JSON objects
    matches = re.finditer(pattern, text_response)
    json_objects = []
    for match in matches:
        json_str = match.group(0)
        try:
            json_obj = json.loads(json_str)
            json_objects.append(json_obj)
        except json.JSONDecodeError:
            extended_json_str = extend_search(text_response, match.span())
            try:
                json_obj = json.loads(extended_json_str)
                json_objects.append(json_obj)
            except json.JSONDecodeError:
                continue
    if json_objects:
        return json_objects
    else:
        return None

# Extends search for nested structures within JSON
def extend_search(text, span):
    start, end = span
    nest_count = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            nest_count += 1
        elif text[i] == '}':
            nest_count -= 1
            if nest_count == 0:
                return text[start:i+1]
    return text[start:end]

# Parsing the resume data using Google Generative AI (Gemini)
def parsed_resume_data(file_path):
    model = genai.GenerativeModel('gemini-1.5-flash')
    sample_file = genai.upload_file(path=file_path, display_name="Resume")
    response = model.generate_content([sample_file, "Give me the data of Name,Email,College,Year of Passout,Degree,Skills from the PDF in JSON Format"])
    json_objects = extract_json(response.text)
    print(json_objects)
    return json_objects

# Creating graph nodes and relationships in Neo4j
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

# Saving parsed data to Neo4j database
def save_db(data):
    print(data['Name'], data['Email'], data['College'], data['Year of Passout'], data['Degree'], data['Skills'])
    with driver.session() as session:
        session.write_transaction(create_graph, str(uuid.uuid4()), data['Name'], data['Email'], data['College'], data['Year of Passout'], data['Degree'], data['Skills'])

# Flask app configuration
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['resume']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Parse resume using Google Generative AI (PaLM API)
        parsed_data = parsed_resume_data(file_path)
        
        if parsed_data:
            # Save to Neo4j database
            save_db(parsed_data[0])
            flash('Resume uploaded and data saved successfully!')
            return redirect(request.url)
        else:
            flash('Failed to parse the resume')
            return redirect(request.url)

@app.route('/candidate/<email>')
def candidate_info(email):
    with driver.session() as session:
        query = "MATCH (c:Candidate {email: $email}) RETURN c"
        result = session.run(query, email=email)
        candidate = result.single()
        
    if candidate:
        candidate_info = candidate['c']
        return render_template('candidate_info.html', candidate=candidate_info)
    else:
        flash('Candidate not found')
        return redirect(url_for('index'))

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
