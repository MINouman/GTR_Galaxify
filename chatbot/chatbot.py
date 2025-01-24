from transformers import GPT2Tokenizer, GPT2LMHeadModel
from sqlalchemy import create_engine, text
import re
import random

tokenizer = GPT2Tokenizer.from_pretrained('distilgpt2')
model = GPT2LMHeadModel.from_pretrained('distilgpt2')

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

DATABASE_URL = 'postgresql://admin:Aikittam1@localhost:5432/samsung_phones'
engine = create_engine(DATABASE_URL)

def clean_input(text):
    """
    Cleans the input text by removing special characters and stripping spaces.
    """
    cleaned_text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return cleaned_text.strip()

def get_phone_spec_response(column, model_name):
    """
    Fetch a specific column (like price_at_launch, release_date, etc.) from the phone_specs table.
    """
    try:
        query = f"SELECT {column} FROM phone_specs WHERE LOWER(model_name) = LOWER(:model_name)"
        with engine.connect() as connection:
            result = connection.execute(text(query), {"model_name": model_name}).fetchone()
            if result:
                return result[0]
            else:
                return None
    except Exception as e:
        print(f"DEBUG: Error in get_phone_spec_response: {e}")
        return None

def generate_gpt_response(input_text):
    """
    Generate a GPT-2 fallback response.
    """
    encoded_input = tokenizer(input_text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    output = model.generate(**encoded_input, max_length=100, num_return_sequences=1)
    response_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return response_text.strip()

def get_response(input_text):
    """
    Generate a chatbot response. Handles database queries for phone specs, comparisons,
    recommendations, and general GPT-2 responses.
    """
    try:
        input_text = input_text.lower().strip()
        print(f"DEBUG: User input received: '{input_text}'")
        if "hi" in input_text or "hello" in input_text:
            return "Hello! Welcome to Galaxify. How can I assist you today? 😊"
        elif "bye" in input_text or "goodbye" in input_text:
            return "Goodbye! Have a wonderful day! 🌟"
        elif "price of" in input_text:
            model_name = clean_input(input_text.split("price of")[1].strip())
            price = get_phone_spec_response("price_at_launch", model_name)
            return f"The price of {model_name} at launch was ${price}." if price else "Sorry, I couldn't find that phone model."
        elif "release date of" in input_text:
            model_name = clean_input(input_text.split("release date of")[1].strip())
            release_date = get_phone_spec_response("release_date", model_name)
            return f"The release date of {model_name} was {release_date}." if release_date else "Sorry, I couldn't find that phone model."
        elif "battery capacity of" in input_text:
            model_name = clean_input(input_text.split("battery capacity of")[1].strip())
            battery_capacity = get_phone_spec_response("battery_capacity", model_name)
            return f"The battery capacity of {model_name} is {battery_capacity} mAh." if battery_capacity else "Sorry, I couldn't find that phone model."
        elif "support expandable storage" in input_text:
            model_name = clean_input(input_text.replace("does", "").replace("support expandable storage", "").strip())
            expandable_storage = get_phone_spec_response("expandable_storage", model_name)
            return f"Yes, {model_name} supports expandable storage." if expandable_storage == "Yes" else f"No, {model_name} does not support expandable storage."
        elif "features of" in input_text:
            model_name = clean_input(input_text.split("features of")[1].strip())
            features = {
                "Price": get_phone_spec_response("price_at_launch", model_name),
                "Battery": get_phone_spec_response("battery_capacity", model_name),
                "Display": get_phone_spec_response("display_size", model_name),
                "Camera": get_phone_spec_response("rear_camera", model_name),
            }
            response = "\n".join([f"{key}: {value}" for key, value in features.items() if value])
            return response if response else "Sorry, I couldn't find features for that model."
        elif "recommend" in input_text and "camera" in input_text:
            budget = float(re.search(r"\d+", input_text).group()) if re.search(r"\d+", input_text) else None
            if budget:
                query = "SELECT model_name FROM phone_specs WHERE price_at_launch <= :budget ORDER BY rear_camera DESC LIMIT 1"
                with engine.connect() as connection:
                    result = connection.execute(text(query), {"budget": budget}).fetchone()
                    if result:
                        return f"I recommend the {result[0]} for a great camera under ${budget}."
            return "Sorry, I couldn't find recommendations within your budget."
        elif "support 5g" in input_text:
            model_name = clean_input(input_text.replace("does", "").replace("support", "").strip())
            sim_specs = get_phone_spec_response("sim_specs", model_name)
            if sim_specs and "5g" in sim_specs.lower():
                return f"Yes, {model_name} supports 5G connectivity."
            else:
                return f"No, {model_name} does not support 5G connectivity."
        elif "which phone has a better" in input_text and "display" in input_text:
            phones = input_text.split(":")[1].strip().split("or")
            if len(phones) == 2:
                phone1, phone2 = clean_input(phones[0]), clean_input(phones[1])
                display1 = get_phone_spec_response("display_size", phone1)
                display2 = get_phone_spec_response("display_size", phone2)
                try:
                    spec1 = float(re.search(r"\d+(\.\d+)?", display1).group()) if display1 else None
                    spec2 = float(re.search(r"\d+(\.\d+)?", display2).group()) if display2 else None
                    better_phone = phone1 if spec1 > spec2 else phone2
                    return f"{better_phone.title()} has a better display."
                except Exception:
                    return "Sorry, I couldn't compare the display sizes."
        elif "good for gaming" in input_text:
            model_name = clean_input(input_text.replace("is", "").replace("good for gaming", "").strip())
            gpu = get_phone_spec_response("gpu", model_name)
            refresh_rate = get_phone_spec_response("refresh_rate", model_name)
            if gpu and refresh_rate:
                return f"Yes, {model_name} is great for gaming with a {gpu} GPU and a {refresh_rate}Hz refresh rate."
            else:
                return f"Sorry, I couldn't find gaming-specific details for {model_name}."
        elif "brief about" in input_text or "tell me about" in input_text:
            model_name = clean_input(input_text.replace("tell me about", "").replace("in brief", "").replace("brief about", "").strip())
            specs = {
                "Price": get_phone_spec_response("price_at_launch", model_name),
                "Release Date": get_phone_spec_response("release_date", model_name),
                "Battery": get_phone_spec_response("battery_capacity", model_name),
                "Chipset": get_phone_spec_response("chipset", model_name),
                "Display": get_phone_spec_response("display_size", model_name),
                "Camera": get_phone_spec_response("rear_camera", model_name),
            }
            if any(specs.values()):
                response = f"Here is a brief about {model_name}:\n"
                response += "\n".join([f"{key}: {value}" for key, value in specs.items() if value])
                return response
            else:
                return "Sorry, I couldn't find that phone model."
        else:
            return generate_gpt_response(input_text)

    except Exception as e:
        print(f"DEBUG: Error occurred: {e}")
        return "Sorry, something went wrong while processing your query."

if __name__ == "__main__":
    queries = [
        "Hi!",
        "What is the price of Samsung Galaxy S24 Ultra?",
        "What is the release date of Samsung Galaxy A55?",
        "Tell me about Samsung Galaxy A55 in brief.",
        "Which phone has a better display: Samsung Galaxy A55 or Samsung Galaxy S24 Ultra?",
        "Does Samsung Galaxy A55 support 5G?",
        "Recommend a phone with a great camera under $500.",
    ]
    for query in queries:
        print(f"User: {query}")
        print(f"Galaxify: {get_response(query)}\n")