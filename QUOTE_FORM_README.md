# Quote Form Integration for Sign-nize Bot

## Overview
This update adds a comprehensive quote/mockup form system to the Sign-nize chatbot. When customers mention "mockup" or "quote", a form popup appears to collect all necessary information for creating accurate quotes and mockups.

## New Features

### 1. Quote Form Modal
- **Trigger**: When users mention "mockup" or "quote" in chat
- **Fields Collected**:
  - Size & Dimensions
  - Material Preference (metal, acrylic, aluminum, vinyl, wood, other)
  - Illumination (no lighting, LED backlit, front lit, halo lit, channel letters)
  - Installation Surface (brick wall, concrete, drywall, metal surface, wood surface, other)
  - City & State
  - Budget Range (under $500 to over $10,000)
  - Placement (indoor, outdoor, both)
  - Deadline (standard 15-17 days, rush 12 days with 25% additional cost, flexible)
  - Additional Notes

### 2. MongoDB Integration
- All quote data is stored in MongoDB
- Session-based storage with email association
- Support for updating existing quotes
- Admin endpoint to view all quotes

### 3. Quote Summary Modal
- Shows filled form data after submission
- Instructions to email logos to info@signize.us
- Option to request changes (reopens form with pre-filled data)

### 4. Enhanced Bot Behavior
- **General Queries**: Bot answers general signage questions using knowledge base
- **Quote Requests**: Bot triggers form when "mockup" or "quote" is mentioned
- **Email Collection**: Still required before quote form can be submitted

## Technical Implementation

### Backend Changes
1. **MongoDB Integration** (`mongodb_operations.py`)
   - MongoDB connection and management
   - CRUD operations for quote data
   - Session-based storage

2. **New API Endpoints** (`app.py`)
   - `/save-quote` - Save quote form data
   - `/get-quote/<session_id>` - Retrieve quote data
   - `/admin/quotes` - Get all quotes (admin)

3. **Updated System Prompt**
   - Modified to handle general queries vs. quote requests
   - Special trigger marker `[QUOTE_FORM_TRIGGER]` for form activation

### Frontend Changes
1. **HTML Modals** (`templates/index.html`)
   - Quote form modal with all required fields
   - Quote summary modal with data display

2. **CSS Styles** (`static/style.css`)
   - Modal overlay and content styles
   - Form styling with focus states
   - Responsive design for mobile

3. **JavaScript Functionality** (`static/script.js`)
   - Form submission and validation
   - Modal show/hide logic
   - Quote data management
   - Integration with chat flow

## Setup Instructions

### 1. Install Dependencies
```bash
pip install pymongo
```

### 2. MongoDB Setup
- Install MongoDB locally or use MongoDB Atlas
- Set `MONGODB_URI` in your `.env` file (optional - defaults to localhost)
- The bot will automatically create the database and collections

### 3. Environment Variables
Add to your `.env` file:
```
MONGODB_URI=mongodb://localhost:27017/
```

## Usage Flow

1. **Customer starts chat** → Bot asks for email
2. **Customer provides email** → Chat becomes active
3. **Customer asks general questions** → Bot answers using knowledge base
4. **Customer mentions "mockup" or "quote"** → Bot triggers quote form
5. **Customer fills form** → Data saved to MongoDB
6. **Form submitted** → Quote summary shown with next steps
7. **Customer can request changes** → Form reopens with pre-filled data

## API Endpoints

### Save Quote
```
POST /save-quote
{
  "session_id": "string",
  "email": "string", 
  "form_data": {
    "sizeDimensions": "string",
    "materialPreference": "string",
    "illumination": "string",
    "installationSurface": "string",
    "cityState": "string",
    "budget": "string",
    "placement": "string",
    "deadline": "string",
    "additionalNotes": "string"
  }
}
```

### Get Quote
```
GET /get-quote/<session_id>
```

### Get All Quotes (Admin)
```
GET /admin/quotes
```

## Database Schema

### Quotes Collection
```json
{
  "_id": "ObjectId",
  "session_id": "string",
  "email": "string",
  "form_data": {
    "sizeDimensions": "string",
    "materialPreference": "string",
    "illumination": "string",
    "installationSurface": "string",
    "cityState": "string",
    "budget": "string",
    "placement": "string",
    "deadline": "string",
    "additionalNotes": "string"
  },
  "created_at": "datetime",
  "updated_at": "datetime",
  "status": "string"
}
```

## Error Handling
- MongoDB connection failures are handled gracefully
- Form validation on both frontend and backend
- User-friendly error messages
- Fallback to local storage if MongoDB unavailable

## Future Enhancements
- Email notifications when quotes are submitted
- Quote status tracking
- Integration with design team workflow
- Analytics dashboard for quote data
