import os
from flask import Flask, render_template, request, flash, redirect, url_for
import openai
import random
import pickle
import uuid
from flask_login import LoginManager, login_user
from secrets import compare_digest
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'data/users.db')

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

DAVINCI = 'text-davinci-003'
CURIE = 'text-curie-001'

common_eye_colors = ["brown", "blue", "green", "hazel", "gray"]
uncommon_eye_colors = ["amber", "violet", "black", "red", "pink"]


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __init__(self, username, email, password_hash, active=True):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.active = active

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)



@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

# Use the API key from your OpenAI account
openai.api_key = os.getenv("API_KEY")

def generate_value_with_api_call(name):

    if name == "weight":
        return random.randint(90,200)

    elif name == "height":
        value = openai.Completion.create(engine=DAVINCI,
                                         prompt="Choose a height in feet for my character.",max_tokens=7,n=1,temperature=0.7)
    elif name == "occupation":
        value = openai.Completion.create(engine=DAVINCI,
                                         prompt="Give me ONE job or occupation",max_tokens=15,n=1,temperature=0.7)
    elif name == "location":
        value = openai.Completion.create(engine=DAVINCI,
                                         prompt="Generate a place that a person could live. ",max_tokens=20,n=1,temperature=0.7)
    elif name == "age":
        value = openai.Completion.create(engine=CURIE,
                                         prompt="Pick a random age (in years) for my character",max_tokens=10,n=1,temperature=0.5)
    elif name == "eye_color":
        value = random.choice(common_eye_colors) if random.randint(1,10) < 7 else random.choice(uncommon_eye_colors)
        return value

    elif name == "hair_color":
        value = openai.Completion.create(engine=CURIE,
                                         prompt=f"Give me one hair color. ",max_tokens=15,n=1,temperature=0.7)
    elif name == "gender":
        value = openai.Completion.create(engine=CURIE,
                                         prompt=f"Pick a gender for my character",max_tokens=15,n=1,temperature=0.7)
    else:
        value = openai.Completion.create(engine=DAVINCI,
                                         prompt=f"What {name} should my character have?", max_tokens=15, n=1,
                                         temperature=0.7)

    print(value.choices[0].text)
    return value.choices[0].text

def generate_random_name():
    value = openai.Completion.create(engine="text-curie-001",
                                     prompt=f"Pick a name for my character. ",
                                     max_tokens=10,
                                     n=1,
                                     temperature=0.8)
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
            hair_color = generate_value_with_api_call("hair_color")
            prompt += f" The character's hair color is {hair_color}."

        if eye_color:
            prompt += f" The character's eye color is {eye_color}."
        else:
            eye_color = generate_value_with_api_call("eye_color")
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

        completions = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=200, n=1,stop=None,temperature=0.7)

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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        email = request.form['email']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("That username is already taken. Please choose a different one.")
            return redirect(url_for('register'))

        # Check if the email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("That email is already taken. Please choose a different one.")
            return redirect(url_for('register'))

        # Check if the passwords match
        if compare_digest(password, password_confirm):
            flash("The passwords do not match.")
            return redirect(url_for('register'))

        # Hash the password
        password_hash = generate_password_hash(password)

        # Create a new user and add it to the database
        new_user = User(username=username, email=email, password_hash=password_hash, active=True)
        db.session.add(new_user)
        db.session.commit()

        # Log the user in
        login_user(new_user)

        return redirect(url_for('index'))

    return render_template('register.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
