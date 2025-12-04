<h1>Amazon Price Tracker<h1/><br>
<img src="result/Screenshot 2025-12-04 234048.png" width="350" />

Users enter the Amazon product URL, the target price, and their email.
The data is saved in JSON.
Every 15 minutes the system checks the product price.
If the price is below or equal to the user’s price, an email is sent, and the item is removed from JSON.

<img src="IMAGE_LINK_HERE" width="350" />
What It Does

User enters URL

User enters price

Auto check every 15 minutes

Sends email when price drops

Removes entry from JSON after email

<img src="result/Screenshot 2025-12-04 234151.png" width="350" />
JSON

Stores: URL, target price, email, ID.

Email

Sent when the product price becomes lower than the user’s entered price.
