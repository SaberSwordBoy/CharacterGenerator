import os
from flask import Flask, render_template, request
import openai
import random
import pickle
import uuid

app = Flask(__name__)

# Use the API key from your OpenAI account
openai.api_key = os.getenv("API_KEY")

def generate_value_with_api_call(name):

    if name == "weight":
        return random.randint(90,200)

    value = openai.Completion.create(engine="text-curie-001",
                                     prompt=f"Please generate ONE random {name}, in third person.",
                                     max_tokens=15,
                                     n=1,
                                     stop=None,
                                     temperature=0.7)
    print(value.choices[0].text)
    return value.choices[0].text

def generate_random_name():
    value = openai.Completion.create(engine="text-curie-001",
                                     prompt=f"Please generate a name for my character!",
                                     max_tokens=15,
                                     n=1,
                                     stop=None,
                                     temperature=0.7)
    print("Generated Name: " + value.choices[0].text)
    return value.choices[0].text

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get user input for the character's name and description
        name = request.form["name"]
        description = request.form["description"]

        # Get user input for other character details
        gender = request.form["gender"]
        age = request.form["age"]
        occupation = request.form["occupation"]
        height = request.form["height"]
        hair_color = request.form["hair_color"]
        eye_color = request.form["eye_color"]
        weight = request.form["weight"]
        location = request.form["location"]

        if not name:
            name = generate_random_name()

        # Use GPT-3 to generate a unique character based on the user's input
        prompt = f"Create a detailed description of an original character named {name}. {description}"

        # Add the other character details to the prompt if provided by the user

        if gender:
            prompt += f" The character's gender is {gender}."
        else:
            gender = generate_value_with_api_call("gender")
            prompt += f" The character's gender is {gender}."

        if age:
            prompt += f" The character's age is {age}."
        else:
            age = generate_value_with_api_call("age")
            prompt += f" The character's age is {age}."

        if occupation:
            prompt += f" The character's occupation is {occupation}."
        else:
            occupation = generate_value_with_api_call("occupation")
            prompt += f" The character's occupation is {occupation}."

        if height:
            prompt += f" The character's height is {height}."
        else:
            height = generate_value_with_api_call("height")
            prompt += f" The character's height is {height}."

        if hair_color:
            prompt += f" The character's hair color is {hair_color}."
        else:
            hair_color = generate_value_with_api_call("hair color")
            prompt += f" The character's hair color is {hair_color}."

        if eye_color:
            prompt += f" The character's eye color is {eye_color}."
        else:
            eye_color = generate_value_with_api_call("eye color")
            prompt += f" The character's eye color is {eye_color}."

        if weight:
            prompt += f" The character's weight is {weight}."
        else:
            weight = generate_value_with_api_call("weight")
            prompt += f" The character's weight is {weight}."

        if location:
            prompt += f" The character is from {location}."
        else:
            location = generate_value_with_api_call("location")
            prompt += f" The character is from {location}."

        completions = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=500, n=1,stop=None,temperature=0.7)

        # Get the generated character
        character = completions.choices[0].text

        character_id = str(uuid.uuid4())
        # save the character object with the unique ID to a file
        with open(f'data/saved_characters/{character_id}.pickle', 'wb') as f:
            pickle.dump(
                {"desc": character,
                 "name": name,
                 "age": age,
                 "weight": weight,
                 "height": height,
                 "location": location,
                 "eye_color": eye_color,
                 "hair_color": hair_color,
                 "occupation": occupation,
                 "id": character_id}, f)

        return render_template("result.html",
                               name=name,
                               age=age,
                               gender=gender,
                               hair_color=hair_color,
                               height=height,
                               eye_color=eye_color,
                               location=location,
                               description=character,
                               weight=weight,
                               id=character_id,
                               occupation=occupation)

    return render_template("index.html")


@app.route('/character/<id>')
def character(id):
    # load the character object from the file
    with open(f'data/saved_characters/{id}.pickle', 'rb') as f:
        data = pickle.load(f)
    return render_template('character.html', character=data)


@app.route('/characters')
def characters():
    characters = []
    for file_name in os.listdir("./data/saved_characters/"):

        if file_name.endswith('.pickle'):
            with open("./data/saved_characters/" + file_name, 'rb') as f:
                characters.append(pickle.load(f))

    return render_template('characters.html', characters=characters)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
