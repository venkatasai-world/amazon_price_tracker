<h1>Amazon Price Tracker<h1/>
<img src="result/Screenshot 2025-12-04 234048.png" width="350" />

Users enter the Amazon product URL, the target price, and their email.
The data is saved in JSON.
Every 15 minutes, the system automatically checks the product price.
If the price is below or equal to the user’s entered price, an email is sent and the item is removed from the JSON file.

What It Does

User enters Amazon product URL

User enters target price

System checks price every 15 minutes

Sends email when the price drops

Removes entry from the JSON file after sending the email

<img src="result/Screenshot 2025-12-04 234151.png" width="350" />
JSON Usage

The JSON file stores:

URL

Target Price

Email

ID

Email Notification

An email is sent automatically when the product price becomes lower than or equal to the target price entered by the user.
