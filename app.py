from flask import Flask, render_template, request, jsonify
import csv
from fuzzywuzzy import fuzz

app = Flask(__name__)

# Load data from your dataset (a CSV file)
def load_dataset(file_path):
    dataset = {}
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            food_name = row['Food']
            dataset[food_name.lower()] = {key.lower(): value for key, value in row.items()}
    return dataset

# Define the path to your CSV file
csv_file_path = 'nutrients.csv'

# Sample dataset (food names and nutritional data)
dataset = load_dataset(csv_file_path)

# Valid nutrients in the dataset
valid_nutrients = dataset[next(iter(dataset))].keys()

def find_matching_food(user_input, dataset):
    food_name_scores = {food: fuzz.partial_ratio(user_input, food) for food in dataset.keys()}
    best_match = max(food_name_scores, key=food_name_scores.get)
    return best_match

def extract_food_and_nutrient(user_input):
    for nutrient in valid_nutrients:
        if nutrient in user_input:
            food_name = user_input.replace(nutrient, '').strip()
            return food_name, nutrient
    return None, None

def generate_nutrition_response(user_input, dataset, valid_nutrients):
    if "You can ask me" in user_input:
        response = user_input
    else:
        food_name, nutrient = extract_food_and_nutrient(user_input)

        if food_name and nutrient:
            food_name = find_matching_food(food_name.lower(), dataset)
            if food_name in dataset:
                nutrient = nutrient.lower()
                if nutrient in valid_nutrients:
                    value = dataset[food_name][nutrient]
                    unit = determine_unit(nutrient)  # Determine the unit based on the nutrient
                    response = f"The {nutrient} content in {food_name} is approximately {value} {unit} per 100 grams."
                else:
                    response = f"I don't have information for {nutrient}. Valid nutrients are: {', '.join(valid_nutrients)}"
            else:
                response = f"I don't have information for {food_name}. Please enter a valid food name."
        else:
            response = "You can ask me grams, calories, protein, fat, saturated fat, fiber, carbohydrates."

    return response

def determine_unit(nutrient):
    # Define units for different nutrients, you can extend this dictionary as needed
    units = {
        "calories": "calories",
        "protein": "grams",
        "fat": "grams",
        "saturated fat": "grams",
        "fiber": "grams",
        "carbohydrates": "grams",
    }
    return units.get(nutrient, "unit")  # Default to "unit" if unit is not specified

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']
    response = generate_nutrition_response(user_input, dataset, valid_nutrients)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run()
