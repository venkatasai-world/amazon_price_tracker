# Amazon Price Tracker 🛒📉

A smart and automated **Amazon Price Tracker** built to help users monitor product prices and receive email alerts when the price drops to their desired amount.

## About the Project

This application allows users to enter an **Amazon product URL**, set a **target price**, and provide their **email address**. The system automatically checks the product price every **15 minutes** and sends an email notification when the price becomes **lower than or equal to the target price**.

After the notification is sent, the tracked item is automatically removed from the JSON file to avoid duplicate alerts.

---

## Features

- 🔗 **Track Amazon Product URLs**
- 💰 **Set Your Target Price**
- 📧 **Email Notification Alerts**
- ⏰ **Automatic Price Checking Every 15 Minutes**
- 💾 **JSON File Storage (No Database Needed)**
- 🗑 **Auto-removes product after successful notification**
- 📱 **Simple and user-friendly interface**

---

## How It Works

1. User enters the **Amazon product URL**
2. User sets their **target price**
3. User provides their **email address**
4. System stores the data in a **JSON file**
5. Every **15 minutes**, the system checks the latest product price
6. If the product price is **less than or equal to the target price**:
   - 📩 Email alert is sent
   - 🗑 Entry is removed from JSON automatically

---

## JSON File Stores

The JSON file keeps track of:

- **Product URL**
- **Target Price**
- **User Email**
- **Unique ID**

---

## Email Notification System

When the tracked product reaches the desired price:

- The system automatically sends an **email notification**
- Alerts the user that the product is now available at the target price
- Removes the product from tracking after sending the email

---

## Tech Stack

- **Python / Flask** – Backend
- **HTML** – Frontend structure
- **CSS** – Styling
- **JavaScript** – User interactions
- **JSON** – Data storage
- **Email Service (SMTP)** – Notifications
- **Scheduler / Background Task** – Automatic price checking

---

## Purpose

This project was created to help users avoid manually checking Amazon product prices repeatedly. It automates the process and ensures users get notified instantly when a product reaches their preferred price.

> Track smart. Save money. Get notified instantly. 🚀
