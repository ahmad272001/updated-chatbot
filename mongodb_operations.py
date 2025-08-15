from pymongo import MongoClient
from datetime import datetime
import os
import json
from environment import load_environment

class MongoDBManager:
    def __init__(self):
        # Load environment variables
        load_environment()
        
        # Get MongoDB connection string from environment or use default
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        
        try:
            self.client = MongoClient(mongodb_uri)
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client['signize_bot']
            self.quotes_collection = self.db['quotes']
            self.connected = True
            print("✅ MongoDB connected successfully")
        except Exception as e:
            print(f"⚠️  MongoDB connection failed: {e}")
            print("   Quote data will be stored locally only")
            self.connected = False
            self.client = None
            self.db = None
            self.quotes_collection = None
    
    def save_quote_data(self, session_id, email, form_data):
        """Save quote/mockup form data to MongoDB"""
        if not self.connected:
            print("⚠️  MongoDB not connected - saving quote data locally")
            return self._save_quote_data_locally(session_id, email, form_data)
        
        try:
            quote_document = {
                "session_id": session_id,
                "email": email,
                "form_data": form_data,
                "created_at": datetime.now(),
                "status": "pending",
                "updated_at": datetime.now()
            }
            
            # Check if quote already exists for this session
            existing_quote = self.quotes_collection.find_one({"session_id": session_id})
            
            if existing_quote:
                # Update existing quote
                result = self.quotes_collection.update_one(
                    {"session_id": session_id},
                    {
                        "$set": {
                            "form_data": form_data,
                            "updated_at": datetime.now()
                        }
                    }
                )
                print(f"✅ Quote data updated for session {session_id}")
                return {"success": True, "action": "updated", "quote_id": str(existing_quote["_id"])}
            else:
                # Insert new quote
                result = self.quotes_collection.insert_one(quote_document)
                print(f"✅ Quote data saved for session {session_id}")
                return {"success": True, "action": "created", "quote_id": str(result.inserted_id)}
                
        except Exception as e:
            print(f"❌ Error saving quote data to MongoDB: {e}")
            print("   Falling back to local storage")
            return self._save_quote_data_locally(session_id, email, form_data)
    
    def get_quote_data(self, session_id):
        """Retrieve quote data for a session"""
        if not self.connected:
            print("⚠️  MongoDB not connected - retrieving quote data from local storage")
            return self._get_quote_data_locally(session_id)
        
        try:
            quote = self.quotes_collection.find_one({"session_id": session_id})
            if quote:
                # Convert ObjectId to string for JSON serialization
                quote["_id"] = str(quote["_id"])
                quote["created_at"] = quote["created_at"].isoformat()
                quote["updated_at"] = quote["updated_at"].isoformat()
                return {"success": True, "quote": quote}
            else:
                return {"success": False, "error": "Quote not found"}
        except Exception as e:
            print(f"❌ Error retrieving quote data from MongoDB: {e}")
            print("   Falling back to local storage")
            return self._get_quote_data_locally(session_id)
    
    def update_quote_status(self, session_id, status):
        """Update quote status"""
        if not self.connected:
            print("⚠️  MongoDB not connected - updating quote status locally")
            return self._update_quote_status_locally(session_id, status)
        
        try:
            result = self.quotes_collection.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "status": status,
                        "updated_at": datetime.now()
                    }
                }
            )
            if result.modified_count > 0:
                print(f"✅ Quote status updated to {status} for session {session_id}")
                return {"success": True}
            else:
                return {"success": False, "error": "Quote not found"}
        except Exception as e:
            print(f"❌ Error updating quote status in MongoDB: {e}")
            print("   Falling back to local storage")
            return self._update_quote_status_locally(session_id, status)
    
    def get_all_quotes(self):
        """Get all quotes (for admin purposes)"""
        if not self.connected:
            print("⚠️  MongoDB not connected - retrieving all quotes from local storage")
            return self._get_all_quotes_locally()
        
        try:
            quotes = list(self.quotes_collection.find().sort("created_at", -1))
            for quote in quotes:
                quote["_id"] = str(quote["_id"])
                quote["created_at"] = quote["created_at"].isoformat()
                quote["updated_at"] = quote["updated_at"].isoformat()
            return {"success": True, "quotes": quotes}
        except Exception as e:
            print(f"❌ Error retrieving all quotes from MongoDB: {e}")
            print("   Falling back to local storage")
            return self._get_all_quotes_locally()

    def _save_quote_data_locally(self, session_id, email, form_data):
        """Save quote data to local JSON file"""
        try:
            # Create quotes directory if it doesn't exist
            os.makedirs("quotes", exist_ok=True)
            
            quote_document = {
                "_id": f"local_{session_id}",
                "session_id": session_id,
                "email": email,
                "form_data": form_data,
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                "updated_at": datetime.now().isoformat()
            }
            
            # Check if quote already exists
            filename = f"quotes/quote_{session_id}.json"
            if os.path.exists(filename):
                # Update existing quote
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                existing_data["form_data"] = form_data
                existing_data["updated_at"] = datetime.now().isoformat()
                quote_document = existing_data
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(quote_document, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Quote data saved locally for session {session_id}")
            return {"success": True, "action": "saved_locally", "quote_id": quote_document["_id"]}
            
        except Exception as e:
            print(f"❌ Error saving quote data locally: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_quote_data_locally(self, session_id):
        """Retrieve quote data from local JSON file"""
        try:
            filename = f"quotes/quote_{session_id}.json"
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    quote_data = json.load(f)
                return {"success": True, "quote": quote_data}
            else:
                return {"success": False, "error": "Quote not found"}
        except Exception as e:
            print(f"❌ Error retrieving quote data locally: {e}")
            return {"success": False, "error": str(e)}
    
    def _update_quote_status_locally(self, session_id, status):
        """Update quote status in local JSON file"""
        try:
            filename = f"quotes/quote_{session_id}.json"
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    quote_data = json.load(f)
                quote_data["status"] = status
                quote_data["updated_at"] = datetime.now().isoformat()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(quote_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Quote status updated locally to {status} for session {session_id}")
                return {"success": True}
            else:
                return {"success": False, "error": "Quote not found"}
        except Exception as e:
            print(f"❌ Error updating quote status locally: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_all_quotes_locally(self):
        """Get all quotes from local JSON files"""
        try:
            quotes = []
            quotes_dir = "quotes"
            if os.path.exists(quotes_dir):
                for filename in os.listdir(quotes_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(quotes_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            quote_data = json.load(f)
                        quotes.append(quote_data)
            
            # Sort by created_at (newest first)
            quotes.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return {"success": True, "quotes": quotes}
        except Exception as e:
            print(f"❌ Error retrieving all quotes locally: {e}")
            return {"success": False, "error": str(e)}

# Global MongoDB manager instance
mongodb_manager = MongoDBManager()
