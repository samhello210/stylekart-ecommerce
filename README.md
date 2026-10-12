# StyleKart

A modern, responsive clothing e-commerce app built with Python and Streamlit, backed by SQLite. It includes a product catalog, shopping cart, checkout flow, customer accounts, admin dashboard, reports, and demo-ready payment handling.

## Features

- Product catalog for men, women, kids, footwear, and accessories
- Search, filter, and sorting
- Detailed product cards with size, color, availability, and discount info
- Persistent shopping cart with quantities and shipping totals
- Registration and secure login using hashed passwords
- Customer profile and order history
- Admin dashboard for inventory, customers, orders, and reports
- Payment flow with Stripe-ready integration and cash on delivery option
- SQLite persistence across app restarts
- Modern, mobile-friendly fashion-store UI

## Project structure

- `app.py` – main Streamlit application
- `requirements.txt` – Python dependencies
- `uploads/` – user-uploaded product images
- `.gitignore` – repository hygiene

## Quick start

1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   streamlit run app.py
   ```
5. Open the URL shown in the terminal (usually http://localhost:8501).

## Database setup

The app automatically creates the SQLite database at startup if it does not already exist.

- Database file: `stylekart.db`
- Tables created automatically:
  - `products`
  - `users`
  - `cart`
  - `orders`
  - `order_items`
- If the database is empty, the app seeds sample products and default demo accounts.

## Demo accounts

Default demo accounts are created on first run:

- Admin: `admin@stylekart.com` / `admin123`
- Customer: `customer@stylekart.com` / `customer123`

## Payment mode

This application is intentionally built in a secure demo-friendly way:

- Raw card details are never stored in SQLite or anywhere else.
- Payment is processed only in a simulated demo mode unless you provide real payment credentials.
- Cash on delivery is available as a supported method.
- For production use, configure Stripe credentials and update the `process_payment` logic in `app.py`.

## Production deployment notes

For real payments and production-grade auth, use:

- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- Environment-based secrets management
- HTTPS-only deployment with secure session handling

## Deployment to Streamlit Cloud

1. Push this repo to GitHub.
2. Log in to Streamlit Community Cloud.
3. Create a new app and point it to this repository.
4. Set `app.py` as the main file.
5. Add environment secrets if you want real payment integration.
6. Deploy.

## Security notes

- Passwords are hashed with Werkzeug.
- Input data is validated before database writes.
- Product and user uploads are stored locally under `uploads/`.
- Card numbers are accepted only as temporary form input and never persisted.

## License

This project is provided for educational and demo purposes.
