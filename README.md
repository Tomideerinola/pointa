
# Pointa

Pointa is a web application for event management, allowing users to browse, book, and manage events while enabling organizers to create events, track bookings, and request payouts. This project was built using Django and Python and includes a complete booking flow, user and organizer dashboards, and advanced filtering for events.

## Table of Contents

- [Features](#features)  
- [Technologies Used](#technologies-used)  
- [Models and Database](#models-and-database)  
- [Functionalities](#functionalities)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Folder Structure](#folder-structure)  
- [Author](#author)

## Features

- User authentication and registration  
- Organizer authentication and registration  
- Event browsing with advanced filters (category, location, price)  
- Event detail pages with ticket selection  
- Booking flow with pending and paid statuses  
- User dashboard showing booked and saved events  
- Organizer dashboard showing created events, total earnings, and payouts  
- Payout request system for organizers  
- Contact form for general inquiries  
- Recent, popular, and upcoming events sections on event list  
- Responsive front-end using Bootstrap  

## Technologies Used

- **Backend:** Python, Django 6.0.2  
- **Database:** SQLite (development)  
- **Frontend:** HTML5, CSS3, Bootstrap 5, Django Template Language  
- **Libraries & Packages:**  
  - `django.contrib.auth` for authentication  
  - `django.db.models` for ORM and aggregations  
  - `django.forms` for forms  
  - `django.contrib.messages` for flash messages  
  - `django.utils.timezone` for date filtering  
- **Version Control:** GitHub  

## Models and Database

Key models in the project:

- **User:** Django built-in User model extended with organizer profile  
- **Organizer:** Linked to a user, manages events and payouts  
- **Event:** Stores event details, category, venue, date, and tickets  
- **Ticket:** Related to events, stores ticket type, price, and quantity  
- **Order:** Stores booking details including status (`pending` or `paid`)  
- **OrderItem:** Links tickets to orders  
- **Payout:** Organizer payouts with status (`pending` or `paid`)  
- **Category:** Event categories  
- **SavedEvent:** Allows users to save favorite events  
- **ContactMessage:** Stores messages submitted from the contact form  

## Functionalities

### Users

- Browse upcoming events filtered by category, location, and price  
- Book tickets for events and view booking confirmation  
- View saved and booked events in the dashboard  
- Submit inquiries through the contact form  

### Organizers

- Create and manage events  
- View total earnings from paid bookings  
- Request payouts for available balances  
- View event performance (recent, popular, upcoming events)  

### Event List

- Three main sections: Upcoming Events, Popular Events (most booked), and Recently Added  
- Filtering by category, city, location, and ticket price  

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/pointa.git
    cd pointa
    ```
2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Apply migrations:
    ```bash
    python manage.py migrate
    ```
5. Create a superuser for admin access:
    ```bash
    python manage.py createsuperuser
    ```
6. Run the development server:
    ```bash
    python manage.py runserver
    ```

## Usage

- Visit `http://127.0.0.1:8000/` in your browser  
- Register as a user or organizer  
- Browse events, book tickets, and manage events through respective dashboards  
- Test the payout system and contact form  

## Folder Structure

## Author

- Developed by Tomide  
- First full-stack Django project completed in February 2026  
- GitHub: [https://github.com/yourusername/pointa](https://github.com/yourusername/pointa)  

---
