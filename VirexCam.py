# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 23:27:32 2026

@author: uobas
"""

from flask import Flask, render_template_string, redirect

app = Flask(__name__)

STRIPE_LINKS = {
    "black_single": {
        "label": "Black",
        "price": "$59.99",
        "url": "https://buy.stripe.com/test_6oU5kF6J84596oR1Db3cc00",
    },
    "white_single": {
        "label": "White",
        "price": "$59.99",
        "url": "https://buy.stripe.com/test_6oU5kF6J84596oR1Db3cc00",
    },
    "bundle_2": {
        "label": "2 For Deal",
        "price": "$99.99",
        "url": "https://buy.stripe.com/6oU5kF6J84596oR1Db3cc00",
    },
    "bundle_3": {
        "label": "3 For Deal",
        "price": "$129.99",
        "url": "https://buy.stripe.com/6oU5kF6J84596oR1Db3cc00",
    },
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
    }

    a { color: inherit; text-decoration: none; }
    img { max-width: 100%; display: block; }

    .announcement {
      background: var(--accent);
      color: white;
      text-align: center;
      padding: 12px 16px;
      font-size: 14px;
      font-weight: 700;
      letter-spacing: 0.4px;
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
    }
  </style>
</head>
<body>
  <div class="announcement">LIMITED-TIME BUNDLE DEALS + FREE SHIPPING</div>

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
            <div class="price" id="displayPrice">$59.99</div>
            <div class="old-price">$79.99</div>
            <div class="save">BUNDLE DEALS AVAILABLE</div>
          </div>

          <ul class="benefits">
            <li>✔ Thumb-sized wearable POV camera for effortless hands-free recording</li>
            <li>✔ Compact clip-on design that sits naturally on your clothing</li>
            <li>✔ Great for content creation, daily moments, travel, cycling, and real-life POV footage</li>
            <li>✔ Available in Black or White, plus 2-pack and 3-pack bundle deals</li>
          </ul>

          <div class="variant-group">
            <div class="variant-label">Choose your option</div>
            <div class="variant-options">
              <button class="variant-btn active" onclick="setVariant(this, 'black_single')">Black</button>
              <button class="variant-btn" onclick="setVariant(this, 'white_single')">White</button>
              <button class="variant-btn" onclick="setVariant(this, 'bundle_2')">2 For Deal</button>
              <button class="variant-btn" onclick="setVariant(this, 'bundle_3')">3 For Deal</button>
            </div>
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
            <p>VirexCam™ is available in Black and White, with bundle options for buying multiple units.</p>
          </div>
          <div class="faq-item">
            <h3>What comes with the offer?</h3>
            <p>Your offer highlights bonus items like SnapClip and Fast Charger, along with included accessories for getting started quickly.</p>
          </div>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer">© 2026 VirexCam™ · Contact · Shipping Policy · Refund Policy · Privacy Policy</footer>

  <div class="sticky-buy">
    <div class="meta">
      <strong>VirexCam™</strong>
      <span id="stickyPrice">$59.99 · Bundle Deals Available</span>
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
      document.getElementById('stickyPrice').textContent = `${variant.price} · Bundle Deals Available`;
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

if __name__ == "__main__":
    app.run(debug=False)