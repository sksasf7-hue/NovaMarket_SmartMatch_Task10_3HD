# NovaMarket SmartMatch - SIT774 Task 10.3HD

NovaMarket SmartMatch is a professional web prototype for **SIT774 Task 10.3HD: Demonstration of Awesome Website Features**. It implements an innovative e-commerce feature named **Adaptive Smart Product Match & Compare Assistant**.

The project demonstrates a functioning website feature, not a static mock-up. Users can enter preferences, receive database-backed recommendations, view transparent score explanations, compare products, save wishlist events, add new demo products, and save contact messages.

## Awesome feature implemented

**Adaptive Smart Product Match** collects user preferences and ranks products using an explainable scoring algorithm. The algorithm combines:

- category fit
- budget fit
- product availability
- user priority: balanced, value, sustainability, performance, or accessibility
- usage profile: study, home office, eco-conscious shopping, or gift buying

Each recommendation includes score bars and reasons so the user understands why a product was suggested.

## Technology stack

- HTML5 semantic interface
- CSS3 responsive glassmorphism design
- JavaScript front-end interactions and Fetch API
- Python 3 standard-library `http.server`
- SQLite embedded database using Python `sqlite3`
- Parameterized SQL for safe inserts

No external web framework is required.

## How to run

```bash
cd NovaMarket_SmartMatch
python app.py
```

Open the browser at:

```text
http://127.0.0.1:8765
```

To rebuild a clean demonstration database:

```bash
python app.py --reset
```

The application creates `novamarket.db` automatically.

## Main files

| File | Purpose |
|---|---|
| `app.py` | Python HTTP server, SQLite schema creation, validation, API endpoints, and SmartMatch scoring logic. |
| `index.html` | Semantic website structure and visible feature tutorial/wiki. |
| `static/styles.css` | Professional responsive visual design, accessibility-focused states, and reduced-motion support. |
| `static/app.js` | SmartMatch form, API calls, product rendering, comparison drawer, wishlist events, and contact form. |
| `schema.sql` | Standalone SQLite schema for documentation and verification. |

## API endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/products` | GET | Returns products, categories, and live metrics. |
| `/api/recommend` | POST | Runs the SmartMatch algorithm and stores a recommendation event. |
| `/api/add-product` | POST | Validates and inserts a product into SQLite. |
| `/api/wishlist` | POST | Saves a wishlist event. |
| `/api/contact` | POST | Validates and stores a contact message. |
| `/api/stats` | GET | Returns live product, recommendation, wishlist, and contact counts. |

## Accessibility and usability notes

- Semantic landmarks and headings are used across the page.
- All form controls have labels.
- Status areas use `aria-live` or `role="status"`.
- Keyboard users can skip to the main feature and operate all controls.
- Focus states are visible.
- The site supports `prefers-reduced-motion`.
- The design is responsive for desktop, tablet, and mobile.

## Suggested GitHub upload steps

```bash
git init
git add .
git commit -m "Implement NovaMarket SmartMatch Task 10.3HD prototype"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/novamarket-smartmatch.git
git push -u origin main
```

After uploading, paste the repository URL into the PDF report.

## Suggested Panopto recording flow

1. Open the website and introduce the feature.
2. Show the SmartMatch form and run a balanced recommendation.
3. Change the priority to accessibility or sustainability to demonstrate adaptive ranking.
4. Explain the score breakdown and reasons.
5. Use the comparison drawer.
6. Save a wishlist event and show live metrics change.
7. Add a demo product and show the catalog update.
8. Save a contact message.
9. Show the key implementation files and explain the scoring function and API endpoints.
10. Conclude with usability, accessibility, performance, and learning points.

The Task 10.3HD video should be no longer than 10 minutes and uploaded to Deakin Panopto with link visibility for Deakin users.
