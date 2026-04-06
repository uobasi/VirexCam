# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 23:27:32 2026

@author: uobas
"""

from flask import Flask, render_template_string, redirect, request, jsonify, session
import stripe
import os
from datetime import datetime, timezone
from google.cloud import firestore
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import time

load_dotenv()

app = Flask(__name__)

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
STRIPE_WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]

EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

app.secret_key = os.environ["FLASK_SECRET_KEY"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if google_creds:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_creds

db = firestore.Client()

def send_order_emails(order):
    total_amount = (order.get("amount_total") or 0) / 100

    shipping = order.get("shipping_address", {}) or {}
    customer_name = order.get("customer_name") or "Customer"
    customer_email = order.get("email")
    product_name = order.get("product_name") or "Your Order"
    quantity = order.get("quantity") or 1
    stripe_session_id = order.get("stripe_session_id", "")

    line1 = shipping.get("line1", "")
    line2 = shipping.get("line2", "")
    city = shipping.get("city", "")
    state = shipping.get("state", "")
    postal_code = shipping.get("postal_code", "")
    country = shipping.get("country", "")

    if not customer_email:
        print("❌ No customer email found on order")
        return False

    # -------------------
    # Customer Email
    # -------------------
    customer_msg = MIMEMultipart("alternative")
    customer_msg["From"] = EMAIL_ADDRESS
    customer_msg["To"] = customer_email
    customer_msg["Subject"] = "Your VirexCam™ order is confirmed"
    customer_msg["Reply-To"] = EMAIL_ADDRESS

    customer_text = f"""
Hi {customer_name},

Thanks for your order with VirexCam™.

Your order has been received and is now being processed.

Order Details
Product: {product_name}
Quantity: {quantity}
Total: ${total_amount:.2f}

Shipping To:
{customer_name}
{line1}
{line2}
{city}, {state} {postal_code}
{country}

We’ll send you another email as soon as your order ships.

Thanks,
VirexCam™ Support
""".strip()

    customer_html = f"""
<!DOCTYPE html>
<html>
  <body style="margin:0;padding:0;background-color:#f6f3ee;font-family:Arial,Helvetica,sans-serif;color:#1f1f1f;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:#f6f3ee;padding:30px 15px;">
      <tr>
        <td align="center">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width:640px;background:#ffffff;border-radius:18px;overflow:hidden;border:1px solid #e9e1d8;">
            <tr>
              <td style="background:#111111;padding:22px 30px;text-align:center;">
                <div style="font-size:26px;font-weight:800;color:#ffffff;">VirexCam™</div>
                <div style="font-size:13px;color:#d7d7d7;margin-top:6px;">Order Confirmation</div>
              </td>
            </tr>

            <tr>
              <td style="padding:34px 30px 10px 30px;">
                <div style="font-size:28px;font-weight:800;line-height:1.2;margin-bottom:12px;">
                  Thanks for your order, {customer_name}!
                </div>
                <div style="font-size:16px;line-height:1.6;color:#555555;">
                  We’ve received your order and it’s now being processed. We’ll send you another email as soon as it ships with your tracking details.
                </div>
              </td>
            </tr>

            <tr>
              <td style="padding:20px 30px;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:#faf7f2;border:1px solid #ebe2d8;border-radius:14px;">
                  <tr>
                    <td style="padding:22px;">
                      <div style="font-size:18px;font-weight:700;margin-bottom:14px;">Order Summary</div>
                      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                        <tr>
                          <td style="padding:8px 0;color:#666666;">Product</td>
                          <td style="padding:8px 0;text-align:right;font-weight:700;">{product_name}</td>
                        </tr>
                        <tr>
                          <td style="padding:8px 0;color:#666666;">Quantity</td>
                          <td style="padding:8px 0;text-align:right;font-weight:700;">{quantity}</td>
                        </tr>
                        <tr>
                          <td style="padding:8px 0;color:#666666;">Total</td>
                          <td style="padding:8px 0;text-align:right;font-weight:700;">${total_amount:.2f}</td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            <tr>
              <td style="padding:0 30px 20px 30px;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:#ffffff;border:1px solid #ebe2d8;border-radius:14px;">
                  <tr>
                    <td style="padding:22px;">
                      <div style="font-size:18px;font-weight:700;margin-bottom:14px;">Shipping Address</div>
                      <div style="font-size:15px;line-height:1.7;color:#444444;">
                        <strong>{customer_name}</strong><br>
                        {line1}<br>
                        {line2 + "<br>" if line2 else ""}
                        {city}, {state} {postal_code}<br>
                        {country}
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            <tr>
              <td style="padding:0 30px 10px 30px;">
                <div style="font-size:15px;line-height:1.7;color:#555555;">
                  Need help? Reply to this email and our team will get back to you as soon as possible.
                </div>
              </td>
            </tr>

            <tr>
              <td style="padding:24px 30px 34px 30px;">
                <div style="font-size:15px;line-height:1.7;color:#555555;">
                  Thanks again for shopping with us,<br>
                  <strong>VirexCam™ Support</strong>
                </div>
              </td>
            </tr>

            <tr>
              <td style="background:#faf7f2;padding:18px 30px;text-align:center;border-top:1px solid #ebe2d8;">
                <div style="font-size:12px;color:#777777;line-height:1.6;">
                  VirexCam™<br>
                  If you have questions about your order, just reply to this email.
                </div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""
    customer_msg.attach(MIMEText(customer_text, "plain"))
    customer_msg.attach(MIMEText(customer_html, "html"))

    # -------------------
    # Admin Email
    # -------------------
    admin_msg = MIMEMultipart()
    admin_msg["From"] = EMAIL_ADDRESS
    admin_msg["To"] = EMAIL_ADDRESS
    admin_msg["Subject"] = "New VirexCam Order Received"
    admin_msg["Reply-To"] = EMAIL_ADDRESS

    stripe_link = f"https://dashboard.stripe.com/test/checkout/sessions/{stripe_session_id}"
    admin_body = f"""
NEW ORDER

Stripe Session ID:
{stripe_session_id}

View in Stripe:
{stripe_link}

Product: {product_name}
Quantity: {quantity}
Total: ${total_amount:.2f}

Customer:
{customer_name}
{customer_email}

Shipping Address:
{line1}
{line2}
{city}, {state} {postal_code}
{country}
""".strip()

    admin_msg.attach(MIMEText(admin_body, "plain"))

    # -------------------
    # Send Emails (with retry)
    # -------------------
    for attempt in range(2):
        server = None
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

            server.send_message(customer_msg)
            server.send_message(admin_msg)

            print("📧 Emails sent successfully")
            return True

        except Exception as e:
            print(f"❌ Email attempt {attempt + 1} failed:", e)
            if attempt == 0:
                time.sleep(5)
            else:
                return False

        finally:
            if server:
                try:
                    server.quit()
                except Exception:
                    pass

    return False

def send_shipping_email(order):
    customer_msg = MIMEMultipart("alternative")
    customer_msg["From"] = EMAIL_ADDRESS
    customer_msg["To"] = order["email"]
    customer_msg["Subject"] = "Your VirexCam™ order has shipped"
    customer_msg["Reply-To"] = EMAIL_ADDRESS

    tracking_number = order.get("tracking_number", "")
    tracking_link = order.get("tracking_link", "")
    customer_name = order.get("customer_name", "Customer")
    product_name = order.get("product_name", "Your order")
    
    tracking_link_html = ""
    if tracking_link:
        tracking_link_html = f"""
        <p style="margin:12px 0 0 0;">
          <a href="{tracking_link}" style="display:inline-block;background:#111111;color:#ffffff;text-decoration:none;padding:12px 18px;border-radius:10px;font-weight:700;">
            Track Your Package
          </a>
        </p>
        """

    text_body = f"""
    Hi {customer_name},
    
    Good news — your order has shipped.
    
    Product: {product_name}
    Tracking Number: {tracking_number}
    Tracking Link: {tracking_link}
    
    We’re excited for it to arrive.
    
    Thanks,
    VirexCam™ Support
    """

    html_body = f"""
    <html>
      <body style="font-family:Arial,Helvetica,sans-serif;background:#f6f3ee;padding:30px;">
        <table style="max-width:640px;margin:0 auto;background:#ffffff;border:1px solid #e9e1d8;border-radius:18px;overflow:hidden;">
          <tr>
            <td style="background:#111111;padding:22px 30px;text-align:center;color:#ffffff;">
              <div style="font-size:26px;font-weight:800;">VirexCam™</div>
              <div style="font-size:13px;color:#d7d7d7;margin-top:6px;">Shipping Confirmation</div>
            </td>
          </tr>
          <tr>
            <td style="padding:30px;">
              <h2 style="margin-top:0;">Your order is on the way, {customer_name}!</h2>
              <p style="color:#555;line-height:1.6;">
                Your order has shipped and is making its way to you.
              </p>
              <div style="background:#faf7f2;border:1px solid #ebe2d8;border-radius:14px;padding:20px;margin-top:20px;">
                <p style="margin:0 0 10px 0;"><strong>Product:</strong> {product_name}</p>
                <p style="margin:0;"><strong>Tracking Number:</strong> {tracking_number}</p>
                {tracking_link_html}
              </div>
              <p style="color:#555;line-height:1.6;margin-top:24px;">
                Thanks again for shopping with us.
              </p>
              
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    customer_msg.attach(MIMEText(text_body, "plain"))
    customer_msg.attach(MIMEText(html_body, "html"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(customer_msg)
    server.quit()


STRIPE_LINKS = {
    "black_single": {
        "label": "Black",
        "price": "$89.99",
        "url": "https://buy.stripe.com/00w00l8RgfNR5kN4Pn3cc04"
    },
    "white_single": {
        "label": "White",
        "price": "$89.99",
        "url": "https://buy.stripe.com/00w00l8RgfNR5kN4Pn3cc04"
    }
}
 
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>VirexCam™ | Ultra-Compact Wearable POV Camera</title>
  <meta name="description" content="VirexCam™ is an ultra-compact wearable POV camera that captures your world in smooth HD, completely hands-free." />
  <style>
    :root {
      --bg: #fffaf5;
      --card: #ffffff;
      --text: #1f1f1f;
      --muted: #6b6b6b;
      --accent: #111111;
      --accent-2: #f4ede4;
      --sale: #b00020;
      --success: #1f7a1f;
      --border: #e8e0d8;
      --shadow: 0 10px 30px rgba(0,0,0,0.08);
      --radius: 18px;
      --max: 1180px;
    }

    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }

    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--text);
      background: var(--bg);
      line-height: 1.5;
    
      /* FIX: prevent sticky bar from covering footer */
      padding-bottom: 120px;
    }

    a { color: inherit; text-decoration: none; }
    img { max-width: 100%; display: block; }

    .announcement {
      background: var(--accent);
      color: white;
      overflow: hidden;
      white-space: nowrap;
      position: relative;
      padding: 12px 0;
      font-size: 14px;
      font-weight: 700;
      letter-spacing: 0.4px;
    }

    .announcement-track {
      display: inline-block;
      padding-left: 100%;
      animation: announcement-scroll 18s linear infinite;
    }

    .announcement:hover .announcement-track {
      animation-play-state: paused;
    }

    @keyframes announcement-scroll {
      0% {
        transform: translateX(0%);
      }
      100% {
        transform: translateX(-100%);
      }
    }

    .navbar {
      position: sticky;
      top: 0;
      z-index: 50;
      background: rgba(255,255,255,0.92);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--border);
    }

    .nav-inner {
      max-width: var(--max);
      margin: 0 auto;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
    }

    .brand {
      font-size: 24px;
      font-weight: 800;
    }

    .nav-links {
      display: flex;
      gap: 24px;
      font-size: 15px;
      color: var(--muted);
    }

    .btn {
      display: inline-block;
      border: none;
      cursor: pointer;
      border-radius: 999px;
      padding: 14px 22px;
      font-weight: 700;
      transition: 0.2s ease;
    }

    .btn-primary {
      background: var(--accent);
      color: white;
      box-shadow: var(--shadow);
    }

    .btn-primary:hover {
      transform: translateY(-1px);
    }

    .container {
      max-width: var(--max);
      margin: 0 auto;
      padding: 0 20px;
    }

    .hero {
      padding: 42px 0 28px;
    }

    .hero-grid {
      display: grid;
      grid-template-columns: 1.05fr 0.95fr;
      gap: 40px;
      align-items: start;
    }

    .gallery {
      display: grid;
      gap: 16px;
    }

    .main-image {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      box-shadow: var(--shadow);
      aspect-ratio: 1 / 1;
    }

    .main-image img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      background: #f4f4f4;
    }

    .thumbs {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }

    .thumbs img {
      border-radius: 14px;
      border: 1px solid var(--border);
      cursor: pointer;
      background: white;
      aspect-ratio: 1 / 1;
      object-fit: contain;
      padding: 8px;
    }

    .product-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 28px;
      box-shadow: var(--shadow);
      position: sticky;
      top: 92px;
    }

    .badge-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 14px;
    }

    .badge {
      background: var(--accent-2);
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 13px;
      font-weight: 700;
    }

    h1 {
      font-size: 42px;
      line-height: 1.08;
      margin: 0 0 10px;
    }

    .subheadline {
      font-size: 18px;
      color: var(--muted);
      margin-bottom: 18px;
    }

    .rating {
      margin: 10px 0 14px;
      font-size: 15px;
      color: var(--muted);
    }

    .price-wrap {
      display: flex;
      align-items: end;
      gap: 12px;
      margin: 16px 0 18px;
      flex-wrap: wrap;
    }

    .price {
      font-size: 34px;
      font-weight: 800;
    }

    .old-price {
      text-decoration: line-through;
      color: var(--muted);
      font-size: 20px;
    }

    .save {
      color: var(--sale);
      font-weight: 800;
      font-size: 15px;
    }

    .benefits {
      display: grid;
      gap: 10px;
      margin: 22px 0;
      padding: 0;
      list-style: none;
    }

    .benefits li {
      background: #faf7f2;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px 14px;
      font-weight: 600;
    }

    .variant-group {
      margin: 22px 0;
    }

    .variant-label {
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 10px;
    }

    .variant-options {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .variant-btn {
      border: 1px solid var(--border);
      background: white;
      padding: 12px 16px;
      border-radius: 999px;
      cursor: pointer;
      font-weight: 700;
    }

    .variant-btn.active {
      background: var(--accent);
      color: white;
      border-color: var(--accent);
    }

    .stock {
      color: var(--success);
      font-weight: 700;
      margin: 12px 0 18px;
      font-size: 14px;
    }

    .checkout-note {
      margin-top: 12px;
      color: var(--muted);
      font-size: 13px;
    }

    .trust-row {
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
      color: var(--muted);
      font-size: 14px;
      margin-top: 18px;
    }

    .section {
      padding: 70px 0;
    }

    .section-alt {
      background: #f8f2eb;
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
    }

    .section h2 {
      text-align: center;
      font-size: 38px;
      margin: 0 0 14px;
    }

    .section .lead {
      max-width: 760px;
      margin: 0 auto 40px;
      text-align: center;
      color: var(--muted);
      font-size: 18px;
    }

    .feature-grid,
    .reviews-grid,
    .faq-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 22px;
    }

    .feature-card,
    .review-card,
    .faq-item {
      background: white;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 24px;
      box-shadow: var(--shadow);
    }

    .review-card p,
    .faq-item p,
    .feature-card p {
      color: var(--muted);
      margin-bottom: 0;
    }

    .sticky-buy {
      position: fixed;
      bottom: 16px;
      left: 50%;
      transform: translateX(-50%);
      width: min(720px, calc(100% - 24px));
      background: rgba(255,255,255,0.96);
      border: 1px solid var(--border);
      border-radius: 999px;
      box-shadow: var(--shadow);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 12px 12px 12px 18px;
      z-index: 60;
    }

    .sticky-buy .meta {
      display: flex;
      flex-direction: column;
    }

    .sticky-buy .meta strong {
      font-size: 15px;
    }

    .sticky-buy .meta span {
      color: var(--muted);
      font-size: 13px;
    }

    .footer {
      padding: 40px 20px 80px;
      color: var(--muted);
      text-align: center;
      font-size: 14px;
    }

    @media (max-width: 980px) {
      .hero-grid,
      .feature-grid,
      .reviews-grid,
      .faq-grid {
        grid-template-columns: 1fr;
      }

      .product-card {
        position: static;
      }

      .nav-links {
        display: none;
      }

      h1 { font-size: 34px; }
      .section h2 { font-size: 30px; }
    }

    @media (max-width: 640px) {
      .thumbs {
        grid-template-columns: repeat(2, 1fr);
      }

      .sticky-buy {
        border-radius: 20px;
        align-items: stretch;
        flex-direction: column;
      }

      .sticky-buy .btn {
        width: 100%;
        text-align: center;
      }

      .announcement {
        font-size: 12px;
        padding: 10px 0;
      }
    }
  </style>
</head>
<body>
  <div class="announcement">
    <div class="announcement-track">
      🚚 FREE SHIPPING • 🔒 SECURE CHECKOUT • 🔥 30% OFF TODAY • 🚚 FREE SHIPPING • 🔒 SECURE CHECKOUT • 🔥 30% OFF TODAY •
    </div>
  </div>

  <nav class="navbar">
    <div class="nav-inner">
      <div class="brand">VirexCam™</div>
      <div class="nav-links">
        <a href="#benefits">Benefits</a>
        <a href="#specs">Specs</a>
        <a href="#features">Features</a>
        <a href="#included">What's Included</a>
        <a href="#faq">FAQ</a>
      </div>
      <a class="btn btn-primary" id="navBuyBtn" href="/buy/black_single">Buy Now</a>
    </div>
  </nav>

  <main>
    <section class="hero container">
      <div class="hero-grid">
        <div class="gallery">
          <div class="main-image">
            <img id="mainProductImage" src="{{ images[0] }}" alt="VirexCam main product image" />
          </div>
          <div class="thumbs">
            {% for image in images %}
            <img src="{{ image }}" alt="VirexCam image {{ loop.index }}" onclick="swapImage(this.src)">
            {% endfor %}
          </div>
        </div>

        <div class="product-card">
          <div class="badge-row">
            <div class="badge">Thumb-Sized POV Camera</div>
            <div class="badge">3 Free Gifts</div>
            <div class="badge">Free Shipping</div>
          </div>

          <h1>Capture Life Hands-Free With VirexCam™</h1>
          <div class="subheadline">
            This ultra-compact wearable POV camera is designed to record your world effortlessly, in stunning clarity.
            Lightweight, discreet, and hands-free, it clips seamlessly onto your clothing so you never miss a moment.
          </div>

          <div class="rating">★★★★★ Simple. Powerful. Always on.</div>

          <div class="price-wrap">
            <div class="price" id="displayPrice">$89.99</div>
            <div class="old-price">$129.99</div>
            <div class="save">30% OFF</div>
            <div class="save">QUANTITY ADJUSTABLE AT CHECKOUT</div>
          </div>

          <ul class="benefits">
            <li>✔ Thumb-sized wearable POV camera for effortless hands-free recording</li>
            <li>✔ Compact clip-on design that sits naturally on your clothing</li>
            <li>✔ Great for content creation, daily moments, travel, cycling, and real-life POV footage</li>
            <li>✔ Available in Black or White with adjustable quantity at checkout</li>
          </ul>

            <div class="variant-group">
              <div class="variant-label">Choose your color</div>
              <div class="variant-options">
                <button class="variant-btn active" onclick="setVariant(this, 'black_single')">Black</button>
                <button class="variant-btn" onclick="setVariant(this, 'white_single')">White</button>
              </div>
            </div>
            
            <div class="checkout-note" style="margin-top: 10px;">
              Quantity can be adjusted securely at checkout.
            </div>

          <div class="stock">In stock — available in Black and White</div>

          <div class="badge-row" style="margin-top:14px; margin-bottom:0;">
            <div class="badge">3 Free Gifts Included</div>
            <div class="badge">SnapClip</div>
            <div class="badge">Fast Charger</div>
          </div>

          <a class="btn btn-primary" id="mainBuyBtn" href="/buy/black_single" style="width:100%; text-align:center; margin-top:18px;">Buy Now</a>
          <div class="checkout-note" id="checkoutNote">Black selected — secure checkout enabled.</div>

          <div class="trust-row">
            <span>Secure Checkout</span>
            <span>Stripe Payment</span>
            <span>Fast Delivery</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="benefits">
      <div class="container">
        <h2>Why VirexCam™ Stands Out</h2>
        <p class="lead">
          VirexCam™ is built around a compact, wearable POV concept: thumb-sized, clip-on, and designed for real moments without bulky gear.
        </p>
        <div class="feature-grid">
          <div class="feature-card">
            <h3>Thumb-Sized & Wearable</h3>
            <p>Built to be ultra-small, easy to wear, and simple to clip on for true POV capture.</p>
          </div>
          <div class="feature-card">
            <h3>Compact Everyday Design</h3>
            <p>At roughly 2.5 × 1.1 × 0.7 inches, it stays discreet and lightweight while still being practical for daily use.</p>
          </div>
          <div class="feature-card">
            <h3>Made for Real-Life POV Moments</h3>
            <p>Use VirexCam™ for creators, travel, commutes, outdoor activities, and everyday documentation.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="specs">
      <div class="container">
        <h2>Quick Product Specs</h2>
        <p class="lead">Simple, compact, and designed to stay out of your way while recording your point of view.</p>
        <div class="feature-grid">
          <div class="feature-card">
            <h3>Video Quality</h3>
            <p>Up to 4K recording with smooth, clear POV footage.</p>
          </div>
          <div class="feature-card">
            <h3>Wide Angle</h3>
            <p>180° ultra-wide field of view for immersive recording.</p>
          </div>
          <div class="feature-card">
            <h3>Waterproof</h3>
            <p>IPX7 waterproof design — ready for outdoor use and tough conditions.</p>
          </div>
          <div class="feature-card">
            <h3>Battery Life</h3>
            <p>Up to 90 minutes of continuous recording with WiFi off.</p>
          </div>
          <div class="feature-card">
            <h3>Storage</h3>
            <p>Supports MicroSD cards for easy storage and transfer.</p>
          </div>
          <div class="feature-card">
            <h3>Size & Weight</h3>
            <p>Ultra-compact at 2.5&quot; × 1.1&quot; × 0.7&quot; and lightweight for daily wear.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="features">
      <div class="container">
        <h2>Built for Real Life</h2>
        <p class="lead">Designed for creators, adventurers, and everyday moments.</p>
        <div class="feature-grid">
          <div class="feature-card">
            <h3>Hands-Free Recording</h3>
            <p>Clip it to your clothes, helmet, bike, or gear and record naturally.</p>
          </div>
          <div class="feature-card">
            <h3>Multiple Mount Options</h3>
            <p>Works great for pockets, bicycles, motorcycles, helmets, walls, and more.</p>
          </div>
          <div class="feature-card">
            <h3>Water Adventure Ready</h3>
            <p>Use it in rugged outdoor conditions, including diving, snorkeling, and surfing with the waterproof case.</p>
          </div>
          <div class="feature-card">
            <h3>Extra-Large Field of View</h3>
            <p>Wide capture makes it easy to record immersive POV footage without missing the action.</p>
          </div>
          <div class="feature-card">
            <h3>Easy File Transfer</h3>
            <p>Transfer footage by app, cable, or SD card to your phone or computer.</p>
          </div>
          <div class="feature-card">
            <h3>Built for Daily Use</h3>
            <p>Lightweight, compact, and easy to carry so you can keep it with you anywhere.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="included">
      <div class="container">
        <h2>What’s Included</h2>
        <p class="lead">Everything you need to start recording right away.</p>
        <div class="feature-grid">
          <div class="feature-card">
            <h3>VirexCam™ Camera</h3>
            <p>Main body camera ready for everyday POV recording.</p>
          </div>
          <div class="feature-card">
            <h3>Mounting Accessories</h3>
            <p>Includes clip, helmet bracket, bicycle bracket, and strap for flexible use.</p>
          </div>
          <div class="feature-card">
            <h3>Waterproof Case</h3>
            <p>Built for wet and rugged environments when adventure calls.</p>
          </div>
          <div class="feature-card">
            <h3>Charging Accessories</h3>
            <p>Includes charging support so you can power up fast and keep going.</p>
          </div>
          <div class="feature-card">
            <h3>Bonus Gifts</h3>
            <p>Offer includes bonus gift messaging such as SnapClip and Fast Charger.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="reviews">
      <div class="container">
        <h2>Why People Love VirexCam™</h2>
        <p class="lead">Replace these with your real customer reviews once you begin collecting orders.</p>
        <div class="reviews-grid">
          <div class="review-card">
            <p>“I wanted something small and easy to wear, and this was exactly it. It makes recording daily moments effortless.”</p>
          </div>
          <div class="review-card">
            <p>“Love how light it feels. I can clip it on and forget it’s there while still capturing everything clearly.”</p>
          </div>
          <div class="review-card">
            <p>“The bundle deal made it worth it for me. I kept one and gave the others away — super convenient little camera.”</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="faq">
      <div class="container">
        <h2>VirexCam™ FAQ</h2>
        <div class="faq-grid">
          <div class="faq-item">
            <h3>How long does shipping take?</h3>
            <p>Shipping times can vary by location, but orders are typically processed quickly and sent out with tracking.</p>
          </div>
          <div class="faq-item">
            <h3>What colors are available?</h3>
            <p>VirexCam™ is available in Black and White. You can adjust quantity during checkout</p>
          </div>
          <div class="faq-item">
            <h3>What comes with the offer?</h3>
            <p>Your offer highlights bonus items like SnapClip and Fast Charger, along with included accessories for getting started quickly.</p>
          </div>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer">© 2026 VirexCam™ <div style="margin-top:40px; font-size:14px;">
  <a href="/shipping-policy">Shipping Policy</a> |
  <a href="/refund-policy">Refund Policy</a> |
  <a href="/contact">Contact</a>
</div></footer>

  <div class="sticky-buy">
    <div class="meta">
      <strong>VirexCam™</strong>
      <span id="stickyPrice">$89.99 · Quantity Adjustable At Checkout</span>
    </div>
    <a class="btn btn-primary" id="stickyBuyBtn" href="/buy/black_single">Buy Now</a>
  </div>

  <script>
    const variants = {{ variants | tojson }};
    let selectedVariant = 'black_single';

    function swapImage(src) {
      document.getElementById('mainProductImage').src = src;
    }

    function setVariant(button, variantKey) {
      document.querySelectorAll('.variant-btn').forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
      selectedVariant = variantKey;
      updateVariantDisplay();
    }

    function updateVariantDisplay() {
      const variant = variants[selectedVariant];
      document.getElementById('displayPrice').textContent = variant.price;
      document.getElementById('stickyPrice').textContent = `${variant.price} · Quantity Adjustable At Checkout`;
      document.getElementById('checkoutNote').textContent = `${variant.label} selected — secure checkout enabled.`;

      const buyHref = `/buy/${selectedVariant}`;
      document.getElementById('mainBuyBtn').href = buyHref;
      document.getElementById('stickyBuyBtn').href = buyHref;
      document.getElementById('navBuyBtn').href = buyHref;
    }
    

    updateVariantDisplay();
  </script>
</body>
</html>
"""



ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>VirexCam Admin Orders</title>
  <style>
    body {
      font-family: Arial, Helvetica, sans-serif;
      margin: 0;
      background: #f7f7f7;
      color: #222;
    }

    .wrap {
      max-width: 1300px;
      margin: 0 auto;
      padding: 24px;
    }

    h1 {
      margin: 0 0 20px;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }

    .count {
      color: #666;
      font-size: 14px;
    }

    .filters {
      background: white;
      border: 1px solid #e7e7e7;
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 18px;
      box-shadow: 0 4px 18px rgba(0,0,0,0.05);
    }

    .filters form {
      display: grid;
      grid-template-columns: 1fr 220px 220px 140px;
      gap: 10px;
    }

    .orders {
      display: grid;
      gap: 18px;
    }

    .card {
      background: white;
      border-radius: 14px;
      padding: 18px;
      box-shadow: 0 4px 18px rgba(0,0,0,0.08);
      border: 1px solid #e7e7e7;
    }

    .card-top {
      display: flex;
      justify-content: space-between;
      align-items: start;
      gap: 16px;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }

    .badge {
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: bold;
      margin-right: 8px;
      margin-bottom: 8px;
      background: #f1f1f1;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(260px, 1fr));
      gap: 16px;
      margin-top: 12px;
    }

    .box {
      background: #fafafa;
      border: 1px solid #ececec;
      border-radius: 10px;
      padding: 14px;
    }

    .label {
      font-size: 12px;
      color: #666;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }

    .value {
      font-size: 14px;
      line-height: 1.5;
      word-break: break-word;
    }

    form.update-form {
      margin-top: 16px;
      display: grid;
      gap: 10px;
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(180px, 1fr));
      gap: 10px;
    }

    input, select, button {
      padding: 10px 12px;
      border-radius: 8px;
      border: 1px solid #d6d6d6;
      font-size: 14px;
    }

    button {
      background: #111;
      color: white;
      border: none;
      cursor: pointer;
      font-weight: bold;
    }

    .empty {
      background: white;
      border-radius: 14px;
      padding: 20px;
      border: 1px solid #e7e7e7;
    }

    .linkbar a {
      text-decoration: none;
      color: #111;
      margin-left: 14px;
    }

    @media (max-width: 900px) {
      .grid, .form-grid, .filters form {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div>
        <h1>Admin Orders</h1>
        <div class="count">{{ orders|length }} order(s)</div>
      </div>
      <div class="linkbar">
        <a href="/">← Back to store</a>
        <a href="/admin/logout">Logout</a>
      </div>
    </div>

    <div class="filters">
      <form method="GET" action="/admin/orders">
        <input type="text" name="q" placeholder="Search name, email, product, tracking..." value="{{ current_q or '' }}">
        
        <select name="status">
          <option value="">All statuses</option>
          <option value="pending" {% if current_status == "pending" %}selected{% endif %}>pending</option>
          <option value="ordered" {% if current_status == "ordered" %}selected{% endif %}>ordered</option>
          <option value="shipped" {% if current_status == "shipped" %}selected{% endif %}>shipped</option>
          <option value="delivered" {% if current_status == "delivered" %}selected{% endif %}>delivered</option>
          <option value="cancelled" {% if current_status == "cancelled" %}selected{% endif %}>cancelled</option>
        </select>

        <select name="sort">
          <option value="newest" {% if current_sort == "newest" %}selected{% endif %}>Most Recent</option>
          <option value="oldest" {% if current_sort == "oldest" %}selected{% endif %}>Oldest</option>
          <option value="amount_high" {% if current_sort == "amount_high" %}selected{% endif %}>Amount High to Low</option>
          <option value="amount_low" {% if current_sort == "amount_low" %}selected{% endif %}>Amount Low to High</option>
        </select>

        <button type="submit">Apply</button>
      </form>
    </div>

    {% if not orders %}
      <div class="empty">No orders found.</div>
    {% else %}
      <div class="orders">
        {% for order in orders %}
          <div class="card">
            <div class="card-top">
              <div>
                <h2 style="margin:0 0 8px;font-size:22px;">{{ order.product_name or "Unknown Product" }}</h2>
                <div>
                  <span class="badge">Qty: {{ order.quantity or 1 }}</span>
                  <span class="badge">Paid: {{ order.payment_status or "unknown" }}</span>
                  <span class="badge">Supplier: {{ order.supplier_status or "pending" }}</span>
                  <span class="badge">
                    {{ order.currency|upper if order.currency else "" }}
                    {{ (order.amount_total / 100) if order.amount_total else "" }}
                  </span>
                </div>
              </div>
              <div style="font-size:13px;color:#666;">
                <div><strong>Doc ID:</strong> {{ order.doc_id }}</div>
                <div><strong>Created:</strong> {{ order.created_at or "" }}</div>
              </div>
            </div>

            <div class="grid">
              <div class="box">
                <div class="label">Customer</div>
                <div class="value">
                  <strong>{{ order.customer_name or "" }}</strong><br>
                  {{ order.email or "" }}<br>
                  {{ order.phone or "" }}
                </div>
              </div>

              <div class="box">
                <div class="label">Shipping Address</div>
                <div class="value">
                  {{ order.shipping_address.line1 if order.shipping_address else "" }}<br>
                  {% if order.shipping_address and order.shipping_address.line2 %}
                    {{ order.shipping_address.line2 }}<br>
                  {% endif %}
                  {{ order.shipping_address.city if order.shipping_address else "" }},
                  {{ order.shipping_address.state if order.shipping_address else "" }}
                  {{ order.shipping_address.postal_code if order.shipping_address else "" }}<br>
                  {{ order.shipping_address.country if order.shipping_address else "" }}
                </div>
              </div>

              <div class="box">
                <div class="label">Stripe</div>
                <div class="value">
                  <strong>Session ID:</strong> {{ order.stripe_session_id or "" }}
                </div>
              </div>

              <div class="box">
              <div class="label">Fulfillment</div>
              <div class="value">
                <strong>Supplier Order ID:</strong> {{ order.supplier_order_id or "" }}<br>
                <strong>Tracking Number:</strong> {{ order.tracking_number or "" }}<br>
                <strong>Tracking Link:</strong>
                {% if order.tracking_link %}
                  <a href="{{ order.tracking_link }}" target="_blank">{{ order.tracking_link }}</a>
                {% else %}
                  N/A
                {% endif %}
              </div>
            </div>
            </div>

            <form class="update-form" method="POST" action="/admin/orders/{{ order.doc_id }}/update">
              <div class="form-grid">
                  <select name="supplier_status">
                    <option value="pending" {% if order.supplier_status == "pending" %}selected{% endif %}>pending</option>
                    <option value="ordered" {% if order.supplier_status == "ordered" %}selected{% endif %}>ordered</option>
                    <option value="shipped" {% if order.supplier_status == "shipped" %}selected{% endif %}>shipped</option>
                    <option value="delivered" {% if order.supplier_status == "delivered" %}selected{% endif %}>delivered</option>
                    <option value="cancelled" {% if order.supplier_status == "cancelled" %}selected{% endif %}>cancelled</option>
                  </select>
                
                  <input
                    type="text"
                    name="supplier_order_id"
                    placeholder="Supplier order ID"
                    value="{{ order.supplier_order_id or '' }}"
                  >
                
                  <input
                    type="text"
                    name="tracking_number"
                    placeholder="Tracking number"
                    value="{{ order.tracking_number or '' }}"
                  >
                
                  <input
                    type="url"
                    name="tracking_link"
                    placeholder="Tracking link"
                    value="{{ order.tracking_link or '' }}"
                  >
                </div>

              <button type="submit">Update Order</button>
            </form>
          </div>
        {% endfor %}
      </div>
    {% endif %}
  </div>
</body>
</html>
"""


ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Admin Login</title>
  <style>
    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: #f7f7f7;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }
    .card {
      background: white;
      padding: 28px;
      border-radius: 14px;
      box-shadow: 0 4px 18px rgba(0,0,0,0.08);
      width: 100%;
      max-width: 380px;
      border: 1px solid #e7e7e7;
    }
    h1 {
      margin-top: 0;
      font-size: 24px;
    }
    p {
      color: #666;
      font-size: 14px;
    }
    input, button {
      width: 100%;
      padding: 12px;
      border-radius: 8px;
      font-size: 14px;
      margin-top: 12px;
      box-sizing: border-box;
    }
    input {
      border: 1px solid #d6d6d6;
    }
    button {
      border: none;
      background: #111;
      color: white;
      font-weight: bold;
      cursor: pointer;
    }
    .error {
      color: #b00020;
      margin-top: 12px;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>Admin Login</h1>
    <p>Enter your admin password to access orders.</p>
    <form method="POST">
      <input type="password" name="password" placeholder="Admin password" required>
      <button type="submit">Login</button>
    </form>
    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route("/")
def home():
    images = [
        "/static/VirexCam-7.jpg",
        "/static/VirexCam-8.jpg",
        "/static/VirexCam-5.jpg",
        "/static/VirexCam-6.jpg",
        "/static/VirexCam-3.jpg",
        "/static/VirexCam-4.jpg",
    ]
    return render_template_string(HTML, variants=STRIPE_LINKS, images=images)

@app.route("/buy/<variant_key>")
def buy(variant_key: str):
    variant = STRIPE_LINKS.get(variant_key)
    if not variant:
        return redirect("/")
    return redirect(variant["url"])


@app.route("/success")
def success():
    return "<h2>Thanks! Your payment was received.</h2>"

@app.route("/cancel")
def cancel():
    return "<h2>Checkout canceled.</h2>"

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin/orders")
@admin_required
def admin_orders():
    status_filter = request.args.get("status", "").strip().lower()
    sort_by = request.args.get("sort", "newest").strip().lower()
    q = request.args.get("q", "").strip().lower()

    if status_filter:
        docs = db.collection("orders").where("supplier_status", "==", status_filter).stream()
    else:
        docs = db.collection("orders").stream()

    orders = []
    for doc in docs:
        item = doc.to_dict()
        item["doc_id"] = doc.id
        orders.append(item)

    if q:
        filtered_orders = []
        for order in orders:
            haystack = " ".join([
                str(order.get("customer_name", "")),
                str(order.get("email", "")),
                str(order.get("product_name", "")),
                str(order.get("tracking_number", "")),
                str(order.get("supplier_order_id", "")),
                str(order.get("stripe_session_id", "")),
            ]).lower()

            if q in haystack:
                filtered_orders.append(order)

        orders = filtered_orders

    if sort_by == "oldest":
        orders.sort(key=lambda x: x.get("created_at", ""))
    elif sort_by == "amount_high":
        orders.sort(key=lambda x: x.get("amount_total", 0) or 0, reverse=True)
    elif sort_by == "amount_low":
        orders.sort(key=lambda x: x.get("amount_total", 0) or 0)
    else:
        orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return render_template_string(
        ADMIN_HTML,
        orders=orders,
        current_status=status_filter,
        current_sort=sort_by,
        current_q=q,
    )

@app.route("/admin/orders/<doc_id>/update", methods=["POST"])
@admin_required
def update_order(doc_id):
    doc_ref = db.collection("orders").document(doc_id)
    doc = doc_ref.get()
    order = doc.to_dict() or {}

    already_sent = order.get("shipping_email_sent", False)

    supplier_status = request.form.get("supplier_status", "").strip()
    supplier_order_id = request.form.get("supplier_order_id", "").strip()
    tracking_number = request.form.get("tracking_number", "").strip()
    tracking_link = request.form.get("tracking_link", "").strip()

    update_data = {
        "supplier_status": supplier_status,
        "supplier_order_id": supplier_order_id,
        "tracking_number": tracking_number,
        "tracking_link": tracking_link,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    doc_ref.update(update_data)

    if supplier_status == "shipped" and tracking_number and not already_sent:
        order.update(update_data)

        try:
            send_shipping_email(order)
            doc_ref.update({"shipping_email_sent": True})
            print("Shipping email sent")
        except Exception as e:
            print("Shipping email error:", e)

    return redirect("/admin/orders")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None

    if request.method == "POST":
        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/admin/orders")
        else:
            error = "Invalid password"

    return render_template_string(ADMIN_LOGIN_HTML, error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect("/admin/login")

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        print("Invalid payload")
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        print("Invalid signature")
        return "Invalid signature", 400

    print("Event received:", event["type"])

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        customer_details = session.get("customer_details", {}) or {}
        collected_info = session.get("collected_information", {}) or {}
        shipping_details = (
            collected_info.get("shipping_details")
            or session.get("shipping_details")
            or {}
        )
        address = shipping_details.get("address", {}) if shipping_details else {}

        # Get product info
        full_session = stripe.checkout.Session.retrieve(
            session["id"],
            expand=["line_items"]
        )
        line_items = full_session.get("line_items", {}).get("data", [])

        product_name = None
        quantity = None

        if line_items:
            first_item = line_items[0]
            product_name = first_item.get("description")
            quantity = first_item.get("quantity")

        # 🚨 FILTER: Only process VirexCam orders
        if not product_name or "virexcam" not in product_name.lower():
            print("🚫 Ignoring non-VirexCam order:", product_name)
            return "IGNORED", 200

        print("✅ Processing VirexCam order:", product_name)

        order_data = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "stripe_session_id": session.get("id"),
            "payment_status": session.get("payment_status"),
            "product_name": product_name,
            "quantity": quantity,
            "customer_name": shipping_details.get("name") or customer_details.get("name"),
            "email": customer_details.get("email"),
            "phone": customer_details.get("phone"),
            "shipping_address": {
                "line1": address.get("line1"),
                "line2": address.get("line2"),
                "city": address.get("city"),
                "state": address.get("state"),
                "postal_code": address.get("postal_code"),
                "country": address.get("country"),
            },
            "amount_total": session.get("amount_total"),
            "currency": session.get("currency"),
            "supplier_status": "pending",
            "supplier_order_id": "",
            "tracking_number": "",
            "tracking_link": "",
            "shipping_email_sent": False,
        }

        db.collection("orders").add(order_data)
        
        email_sent = send_order_emails(order_data)

        if email_sent:
            print("✅ SAVED TO FIRESTORE + EMAIL SENT")
        else:
            print("⚠️ SAVED TO FIRESTORE, BUT EMAIL FAILED")
            print(order_data)

    return "OK", 200

@app.route("/shipping-policy")
def shipping_policy():
    return render_template_string("""
    <h1>Shipping Policy</h1>

    <h3>Estimated Delivery Times</h3>
    <ul>
        <li>United States: 7–10 business days</li>
        <li>International: 10–20 business days</li>
    </ul>

    <p>Tracking information will be provided once your order has shipped.</p>

    <p>Please note: Shipping times may vary depending on demand and location.</p>

    <h3>Order Processing</h3>
    <p>All orders are processed within 1 business days. Orders are not shipped on weekends or holidays.</p>

    <h3>Lost or Delayed Packages</h3>
    <p>If your order is significantly delayed, please contact us and we will assist you.</p>

    <p><a href="/">← Back to store</a></p>
    """)
    
    
@app.route("/refund-policy")
def refund_policy():
    return render_template_string("""
    <h1>Refund Policy</h1>

    <p>We offer a 10-day refund policy from the date of delivery.</p>

    <h3>Eligibility</h3>
    <ul>
        <li>Item must be unused and in original condition</li>
        <li>Proof of purchase required</li>
    </ul>

    <h3>Non-Refundable Situations</h3>
    <ul>
        <li>Items damaged due to misuse</li>
        <li>Items returned after 10 days</li>
    </ul>

    <h3>Refund Process</h3>
    <p>To request a refund, contact us at the email below. Once approved, refunds are processed back to your original payment method within 5–10 business days.</p>

    <h3>Exchanges</h3>
    <p>If your item arrives defective or damaged, we will replace it at no additional cost.</p>

    <h3>Contact</h3>
    <p>Email: vibeandvisioninc@gmail.com</p>

    <p><a href="/">← Back to store</a></p>
    """)
    
@app.route("/contact")
def contact():
    return render_template_string("""
    <h1>Contact Us</h1>

    <p>If you have any questions about your order, feel free to reach out.</p>

    <h3>Email Support</h3>
    <p>vibeandvisioninc@gmail.com</p>

    <h3>Response Time</h3>
    <p>We typically respond within 24–48 hours.</p>

    <p><a href="/">← Back to store</a></p>
    """)
    

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)