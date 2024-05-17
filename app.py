# Import libraries
from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

df = pd.read_csv('venv/output_dataset.csv')



def calculate_dashboard_data(data):
    data['Price'] = data['Price'].replace('[^\d.]', '', regex=True).astype(float)

    total_listings = len(data)
    average_price = data['Price'].mean()


    return {
        "total_listings": total_listings,
        "average_price": round(average_price, 2),
    }


dashboard_data = calculate_dashboard_data(df)


def generate_response(user_input):

    user_input_lower = user_input.lower()

    if 'hello' in user_input_lower:
        return "Hello! I'm a mobile chatbot. How can I assist you today?"

    elif 'cheapest' in user_input_lower:
        cheapest_mobile = df.loc[df['Price'].idxmin()]
        return f"The cheapest mobile (ID: {cheapest_mobile['ID']}) is {cheapest_mobile['Name']} by {cheapest_mobile['Brand']} priced at ${cheapest_mobile['Price']}."

    elif 'most expensive' in user_input_lower:
        most_expensive_mobile = df.loc[df['Price'].idxmax()]
        return f"The most expensive mobile (ID: {most_expensive_mobile['ID']}) is {most_expensive_mobile['Name']} by {most_expensive_mobile['Brand']} priced at ${most_expensive_mobile['Price']}."

    elif 'brands' in user_input_lower:
        unique_brands = df['Brand'].unique()
        return f"We have mobile phones from the following brands: {', '.join(unique_brands)}."

    elif 'name of mobile with id' in user_input_lower:
        mobile_id = next((word for word in user_input_lower.split() if word.isdigit()), None)
        if mobile_id is not None:
            mobile_info = df[df['ID'] == int(mobile_id)]
            if not mobile_info.empty:
                return f"The name of mobile ID {mobile_id} is {mobile_info['Name'].iloc[0]}."
            else:
                return f"No mobile found with ID {mobile_id}."
        else:
            return "I couldn't understand the specified mobile ID. Please provide it in the format 'name of mobile with id [ID]'."

    elif 'between' in user_input_lower and 'and' in user_input_lower:
        try:
            _, price1, _, price2 = user_input_lower.split()
            price1, price2 = float(price1), float(price2)
            mobiles_between_prices = df[(df['Price'] >= price1) & (df['Price'] <= price2)]
            return format_mobile_response(mobiles_between_prices, f"Mobiles between ${price1} and ${price2}")
        except ValueError:
            return "I couldn't understand the price range. Please provide it in the format 'between [price1] and [price2]'."

    elif 'over' in user_input_lower and 'price' in user_input_lower:
        try:
            over_price = float(user_input_lower.split()[-1])
            mobiles_over_price = df[df['Price'] > over_price]
            return format_mobile_response(mobiles_over_price, f"Mobiles priced over ${over_price}")
        except ValueError:
            return "I couldn't understand the specified price. Please provide it in the format 'over [price]'."

    elif 'under' in user_input_lower and 'price' in user_input_lower:
        try:
            under_price = float(user_input_lower.split()[-1])
            mobiles_under_price = df[df['Price'] < under_price]
            return format_mobile_response(mobiles_under_price, f"Mobiles priced under ${under_price}")
        except ValueError:
            return "I couldn't understand the specified price. Please provide it in the format 'under [price]'."


    else:
        return "I’m not sure how to respond to that."


def format_mobile_response(mobiles_df, message):
    if not mobiles_df.empty:
        return f"{message}:\n{mobiles_df.to_string(index=False)}\n\n"
    else:
        return f"No mobiles found within the specified range."


# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def start_page():
    user_input = ""
    bot_response = ""

    if request.method == 'POST':
        user_input = request.form['user_input']
        bot_response = generate_response(user_input)
    return render_template('home.html', user_input=user_input, bot_response=bot_response, dashboard_data=dashboard_data)


# Run the app if the script is executed
if __name__ == '__main__':
    app.run(debug=True)
