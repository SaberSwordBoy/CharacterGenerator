import os
from flask import Flask, render_template, request, session, abort, redirect, url_for
import openai
import random
import pickle
import uuid
import logging
from dotenv import load_dotenv
import datetime
from csv import writer
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import requests

from google_auth_oauthlib.flow import Flow

<<<<<<< HEAD
load_dotenv()

#os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

API_USAGE_FILE = "./data/api_usage.csv"

GOOGLE_CLIENT_ID = "729149519506-komgd331r8p7pjjpcsm3klpa4huqoeb8.apps.googleusercontent.com"
=======
from config import *

load_dotenv()
>>>>>>> 9623120fa03ccb4c7680a86b3414a4e700c6bd05

logging.basicConfig(filename="./logs/visits.log",
                    filemode='a',
                    format='%(asctime)s,$(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Server file started...")

app = Flask(__name__)
app.secret_key = "penis-hat-and-balls"

DAVINCI = 'text-davinci-003'
CURIE = 'text-curie-001'

common_eye_colors = ["brown", "blue", "green", "hazel", "gray"]
uncommon_eye_colors = ["amber", "violet", "black", "red", "pink"]

# Use the API key from your OpenAI account
openai.api_key = os.getenv("API_KEY")

client_secrets_file = os.path.join(os.getcwd(), "client_secret.json")

flow = Flow.from_client_secrets_file(client_secrets_file=client_secrets_file,
<<<<<<< HEAD
                                     scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
                                     redirect_uri="https://sab3r.ml/redirect",
                                    )
=======
                                     scopes=["https://www.googleapis.com/auth/userinfo.profile",
                                             "https://www.googleapis.com/auth/userinfo.email", "openid"],
                                     redirect_uri=REDIRECT_URI)

>>>>>>> 9623120fa03ccb4c7680a86b3414a4e700c6bd05

def generate_value_with_api_call(name):
    # logging.info(f"Generating {name}")
    if name == "weight":
        return random.randint(90, 200)

    elif name == "height":
        value = openai.Completion.create(engine=DAVINCI,
                                         prompt="Choose a height in feet for my character.", max_tokens=7, n=1,
                                         temperature=0.7)
    elif name == "occupation":
        value = openai.Completion.create(engine=DAVINCI,
                                         prompt="Give me ONE job or occupation", max_tokens=15, n=1, temperature=0.7)
    elif name == "location":
        value = openai.Completion.create(engine=DAVINCI,
                                         prompt="Generate a place that a person could live. ", max_tokens=20, n=1,
                                         temperature=0.7)
    elif name == "age":
        value = openai.Completion.create(engine=CURIE,
                                         prompt="Pick a random age (in years) for my character", max_tokens=3, n=1,
                                         temperature=0.5)
    elif name == "eye_color":
        value = random.choice(common_eye_colors) if random.randint(1, 10) < 7 else random.choice(uncommon_eye_colors)
        return value

    elif name == "hair_color":
        value = openai.Completion.create(engine=CURIE,
                                         prompt=f"Give me one hair color. ", max_tokens=4, n=1, temperature=0.7)
    elif name == "gender":
        value = openai.Completion.create(engine=CURIE,
                                         prompt=f"Pick a gender for my character", max_tokens=2, n=1, temperature=0.4)
    else:
        value = openai.Completion.create(engine=DAVINCI,
                                         prompt=f"What {name} should my character have?", max_tokens=15, n=1,
                                         temperature=0.7)

    token_usage = value.usage["total_tokens"]
    print(value.choices[0].text)

    with open(API_USAGE_FILE, "a") as file:
        writer_obj = writer(file)
        writer_obj.writerow([datetime.datetime.now(), token_usage, f"Generated {name}"])

    return value.choices[0].text


def generate_random_name(gender: None):
    if gender:
        value = openai.Completion.create(engine="text-curie-001",
                                         prompt=f"Pick a {gender} name for my character",
                                         max_tokens=5,
                                         n=1,
                                         temperature=0.9)
    else:
        value = openai.Completion.create(engine="text-curie-001",
                                         prompt=f"Pick a name for my character",
                                         max_tokens=5,
                                         n=1,
                                         temperature=0.9)

    # print("Generated Name: " + value.choices[0].text)

    token_usage = value.usage["total_tokens"]

    with open(API_USAGE_FILE, "a") as file:
        writer_obj = writer(file)
        writer_obj.writerow([datetime.datetime.now(), token_usage, f"Generated Name {value.choices[0].text}"])

    return value.choices[0].text


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)

        else:
            return function()

    wrapper.__name__ = function.__name__
    return wrapper


@app.route("/chargen", methods=["GET", "POST"])
@login_is_required
def generator():
    logging.info(f"{request.remote_addr} {request.method} requested /")
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
            if gender:
                name = generate_random_name(gender)
            else:
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

        completions = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=200, n=1, stop=None,
                                               temperature=0.7)

        token_usage = completions.usage["total_tokens"]

        with open(API_USAGE_FILE, "a") as file:
            writer_obj = writer(file)
            writer_obj.writerow([datetime.datetime.now(), token_usage, "Generated Character"])

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

    return render_template("generator.html")


@app.route('/character/<id>')
def character(id):
    # logging.info(f"{request.remote_addr} requested /character/{id}")
    # load the character object from the file

    if len(id) != 36:
        abort(501)

    with open(f'data/saved_characters/{session["google_id"]}/{id}.pickle', 'rb') as f:
        data = pickle.load(f)
    return render_template('character.html', character=data)


@app.route('/characters')
@login_is_required
def characters():
    # logging.info(f"{request.remote_addr} requested /characters/")
    characters = []
    user_id = session["google_id"]
    for file_name in os.listdir(f"./data/saved_characters/{user_id}"):
        if file_name.endswith('.pickle'):
            with open(f"./data/saved_characters/{user_id}/" + file_name, 'rb') as f:
                characters.append(pickle.load(f))

    message = False
    if not characters:
        message = True

    return render_template('characters.html', characters=characters, message=message)


@app.route("/about")
def about():
    # logging.info(f"{request.remote_addr} requested /about/")
    return render_template("about.html")


@app.route("/usage")
def api_usage():
    csv_data = open("./data/api_usage.csv", "r").read()

    with open("./data/old_api_usage.csv", "a+") as file:
        writerobj = writer(file)
        writerobj.writerows(csv_data)

    return csv_data


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state

    return redirect(authorization_url)


@app.route("/redirect")
def callback():
    flow.fetch_token(authorization_response=request.url)

    print(session["state"], request.args["state"])

    if not session["state"] == request.args["state"]:
        abort(500)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")

    if not os.path.exists(f"./data/saved_characters/{session['google_id']}"):
        os.mkdir(f"./data/saved_characters/{session['google_id']}")

        with open("./data/users.csv", "a") as file:
            writer_obj = writer(file)
            writer_obj.writerow([datetime.datetime.now(), session["name"], session["email"]])

    return redirect(url_for("generator"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/profile")
def profile():
    return render_template("profile.html", name=session["name"], email=session["email"])


@app.route("/")
def home():
    if "google_id" not in session:
        return render_template("index.html")

    return redirect(url_for("generator"))


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
