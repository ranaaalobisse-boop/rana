# Luxury Jewelry E-commerce API

Backend API for a Jewelry E-commerce and AI Design Platform built with FastAPI, MySQL, and Google Gemini AI.

## Features

- **Authentication**: JWT-based authentication with user registration and login
- **E-commerce**: Product catalog, shopping cart, and order management
- **Admin Dashboard**: CRUD operations for products, categories, jewelers, and payment methods
- **AI Design**: Generate custom jewelry designs using Google Gemini AI
- **Custom Design Requests**: Users can request custom designs from jewelers

## Technology Stack

- **Framework**: FastAPI (Python)
- **Database**: SQLite (No XAMPP required!)
- **ORM**: SQLAlchemy
- **Authentication**: JWT (python-jose, passlib)
- **AI Integration**: Google Gemini API
- **Documentation**: Automatic API docs at `/docs`

## Project Structure

```
backend/
├── main.py                    # Application entry point
├── database.py                # SQLAlchemy configuration
├── models/                    # Database models
├── schemas/                   # Pydantic schemas
├── routers/                   # API endpoints
├── services/                  # External services (Gemini AI)
├── static/                    # Static files (generated designs)
├── uploads/                   # Uploaded files
├── seeder.py                  # Database seeding script
├── requirements.txt           # Python dependencies
└── .env.example               # Environment variables template
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- No database server required! (Uses SQLite)

### 2. Install Dependencies

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
# Required variables:
# - SECRET_KEY (change for production)
# - GEMINI_API_KEY (get from Google AI Studio) - Optional for AI feature
```

**Get Gemini API Key (Optional):**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy it to your `.env` file: `GEMINI_API_KEY=your-key-here`

### 4. Initialize Database

```bash
# Run the database seeder (creates SQLite database + sample data)
python seeder.py
```

When prompted, type `yes` to populate the database with sample data:
- 3 Admin users (admin1, admin2, admin3)
- 2 Customer users (customer1, customer2)
- 3 Jewelers
- 2 Payment Methods
- 4 Main Categories + 12 Subcategories
- 10 Products

The SQLite database file `jewelry.db` will be created automatically in the backend folder.

### 5. Start the Server

```bash
# Development mode with auto-reload
python main.py

# OR using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

Interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Default Login Credentials

### Admin Users
- **admin1** / admin123
- **admin2** / admin123
- **admin3** / admin123

### Customer Users
- **customer1** / customer123
- **customer2** / customer123

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login (returns JWT token) |
| GET | `/api/auth/me` | Get current user info |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List all products (with filters) |
| GET | `/api/products/{id}` | Get product details |
| GET | `/api/products/categories/all` | List all categories |
| GET | `/api/products/featured/list` | Get featured products |

### Cart & Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cart/` | View cart |
| POST | `/api/cart/items` | Add to cart |
| PUT | `/api/cart/items/{id}` | Update quantity |
| DELETE | `/api/cart/items/{id}` | Remove from cart |
| DELETE | `/api/cart/` | Clear cart |
| GET | `/api/orders/payment-methods` | List payment methods |
| POST | `/api/orders/checkout` | Checkout (cart → order) |
| GET | `/api/orders/` | List my orders |
| GET | `/api/orders/{id}` | Get order details |

### AI Design
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/generate-design` | Generate jewelry design with AI |
| GET | `/api/ai/my-designs` | List my generated designs |
| POST | `/api/ai/design-requests` | Submit custom design request |
| GET | `/api/ai/my-design-requests` | List my design requests |

### Admin (requires admin user)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/admin/jewelers` | Manage jewelers |
| GET/POST | `/api/admin/categories` | Manage categories |
| POST | `/api/admin/products` | Create product |
| PUT/DELETE | `/api/admin/products/{id}` | Update/Delete product |
| GET/POST | `/api/admin/payment-methods` | Manage payment methods |
| GET | `/api/admin/orders` | List all orders |
| PUT | `/api/admin/orders/{id}/status` | Update order status |
| GET/PUT | `/api/admin/design-requests` | Manage design requests |

## Frontend Integration Guide

### Using JavaScript Fetch API

#### 1. Authentication

```javascript
// Register a new user
async function register(userData) {
    const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
    });
    return await response.json();
}

// Login and get JWT token
async function login(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    });
    const data = await response.json();
    // Store the token
    localStorage.setItem('token', data.access_token);
    return data;
}

// Make authenticated request
async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    return response;
}
```

#### 2. Products

```javascript
// Get all products
async function getProducts(filters = {}) {
    const queryParams = new URLSearchParams(filters);
    const response = await fetch(`http://localhost:8000/api/products/?${queryParams}`);
    return await response.json();
}

// Get single product
async function getProduct(productId) {
    const response = await fetch(`http://localhost:8000/api/products/${productId}`);
    return await response.json();
}

// Get categories
async function getCategories() {
    const response = await fetch('http://localhost:8000/api/products/categories/all');
    return await response.json();
}
```

#### 3. Cart

```javascript
// Get cart
async function getCart() {
    const response = await fetchWithAuth('http://localhost:8000/api/cart/');
    return await response.json();
}

// Add to cart
async function addToCart(productId, quantity = 1) {
    const response = await fetchWithAuth('http://localhost:8000/api/cart/items', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id: productId, quantity })
    });
    return await response.json();
}

// Remove from cart
async function removeFromCart(itemId) {
    const response = await fetchWithAuth(`http://localhost:8000/api/cart/items/${itemId}`, {
        method: 'DELETE'
    });
    return await response.json();
}
```

#### 4. AI Design Generation

```javascript
// Generate AI jewelry design
async function generateDesign(designOptions) {
    const response = await fetchWithAuth('http://localhost:8000/api/ai/generate-design', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            type: "Ring",           // Ring, Necklace, Bracelet, Earrings
            color: "Gold",          // Gold, Silver, Rose Gold
            shape: "Round",         // Round, Square, Oval, Heart
            material: "Gold",       // Silver, Gold, Platinum
            karat: "18k",          // 18k, 21k, 24k
            gemstone_type: "Diamond", // Diamond, Ruby, Sapphire, None
            gemstone_color: "White"   // White, Red, Blue, Green
        })
    });
    const data = await response.json();
    
    if (data.success) {
        // Display generated image
        const imageUrl = `http://localhost:8000${data.image_url}`;
        console.log('Design generated:', imageUrl);
        return imageUrl;
    } else {
        console.error('Generation failed:', data.message);
    }
}
```

#### 5. Checkout

```javascript
// Get payment methods
async function getPaymentMethods() {
    const response = await fetch('http://localhost:8000/api/orders/payment-methods');
    return await response.json();
}

// Checkout
async function checkout(paymentMethodId, shippingAddress) {
    const response = await fetchWithAuth('http://localhost:8000/api/orders/checkout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            payment_method_id: paymentMethodId,
            shipping_address: shippingAddress
        })
    });
    return await response.json();
}
```

### Using Axios

```javascript
// Configure axios
const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    }
});

// Add auth token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Usage
const products = await api.get('/api/products/');
const cart = await api.get('/api/cart/');
const design = await api.post('/api/ai/generate-design', designOptions);
```

## Database Schema

### Tables

1. **users** - Registered users
2. **jewelers** - Jewelry stores/craftsmen
3. **payment_methods** - Available payment options
4. **categories** - Product categories (hierarchical)
5. **products** - Jewelry products
6. **product_images** - Multiple images per product
7. **product_categories** - Many-to-many relationship
8. **carts** - Shopping carts
9. **cart_items** - Items in carts
10. **orders** - Customer orders
11. **order_items** - Items in orders
12. **user_generated_designs** - AI-generated designs
13. **design_requests** - Custom design requests to jewelers

## Troubleshooting

### Database Issues
```
Error: Database locked or busy
```
- SQLite file `jewelry.db` might be in use by another process
- Close any other Python scripts using the database
- If needed, delete `jewelry.db` and re-run seeder

### CORS Issues
CORS is already configured to allow all origins. If issues persist:
- Check browser console for errors
- Verify request headers include proper Content-Type

### Gemini API Issues
```
Failed to generate design. Please check Gemini API configuration.
```
- Verify `GEMINI_API_KEY` is set in `.env`
- Check API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Model used: `gemini-2.0-flash-exp-image-generation`

## License

MIT License

## Support

For issues or questions, please check the API documentation at `/docs` when the server is running.
