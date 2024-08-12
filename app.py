from flask import Flask, request, jsonify, render_template, session
import openai
import plantuml
import os

app = Flask(__name__)

# Retrieve the secrets from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
flask_secret_key = os.getenv('FLASK_SECRET_KEY')

# # Set the retrieved secrets 
app.secret_key = flask_secret_key
openai.api_key = openai_api_key

def get_uml_from_gpt(description, previous_uml):

    if previous_uml:
        combined = f"{previous_uml}\n{description}"
    else:
        combined = description

    # Call the OpenAI API to generate UML code
    chat_completion = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": f"Based on the previous UML and new description, generate UML code only based on this description: {combined}.  The output should be in proper PlantUML syntax and should not include any markdown formatting.",
            }
        ]
    )
    
    uml_code = chat_completion.choices[0].message.content.strip()
    return uml_code

def compress_and_encode_uml(uml_code):
    plantuml_url = plantuml.PlantUML(url="http://www.planttext.com/api/plantuml/png/")
    
    # Get the image URL from the PlantUML server
    image_url = plantuml_url.get_url(uml_code)
    return image_url

@app.route('/generate-uml', methods=['POST'])
def generate_uml():
    data = request.json
    description = data.get('description', '')
    
    if not description:
        return jsonify({"error": "Description is required"}), 400
    
    #get history from session
    previous_uml = session.get('previous_uml', [])
    
    # Get UML code from GPT
    uml_code = get_uml_from_gpt(description, previous_uml)

    #save updated history back to session
    session['previous_uml'] = uml_code
    
    # Compress and encode the UML code for Planttext
    diagram_url = compress_and_encode_uml(uml_code)
    
    return jsonify({'diagramUrl': diagram_url, 'uml_code': uml_code})

@app.route('/reset-history', methods=['POST'])
def reset_history():
    # Clear the UML history in the session
    session.pop('uml_history', None)
    return jsonify({"message": "History cleared"})

@app.route('/')
def index():
    return render_template('diagramfrontend.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)