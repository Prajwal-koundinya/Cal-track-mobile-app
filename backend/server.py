from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
import os
import logging
import uuid
import base64
import io
from PIL import Image
import asyncio

# Import emergent integrations
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'calorie_tracker')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Initialize FastAPI
app = FastAPI(title="Indian Calorie Tracker API")
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class NutritionalInfo(BaseModel):
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    fiber_per_100g: float

class IndianFood(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    name: str
    category: str  # rice, dal, vegetable, meat, snack, etc.
    region: str  # north, south, east, west
    nutritional_info: NutritionalInfo
    description: Optional[str] = None

class MealEntry(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    user_id: str = "default_user"
    food_name: str
    estimated_quantity: float  # in grams
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    image_base64: Optional[str] = None
    ai_analysis: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    meal_type: str = "general"  # breakfast, lunch, dinner, snack

class MealAnalysisRequest(BaseModel):
    image_base64: str
    description: Optional[str] = None

class ProteinRecommendation(BaseModel):
    recommended_daily_protein: float
    current_protein: float
    deficit: float
    high_protein_foods: List[str]
    meal_suggestions: List[str]

# Initialize Indian foods database
indian_foods_db = [
    {
        "name": "Basmati Rice (cooked)",
        "category": "grain",
        "region": "north",
        "nutritional_info": {
            "calories_per_100g": 121,
            "protein_per_100g": 2.6,
            "carbs_per_100g": 25,
            "fat_per_100g": 0.4,
            "fiber_per_100g": 0.4
        }
    },
    {
        "name": "Dal (Toor/Arhar)",
        "category": "dal",
        "region": "all",
        "nutritional_info": {
            "calories_per_100g": 343,
            "protein_per_100g": 22.3,
            "carbs_per_100g": 59.8,
            "fat_per_100g": 1.5,
            "fiber_per_100g": 9.5
        }
    },
    {
        "name": "Paneer",
        "category": "dairy",
        "region": "north",
        "nutritional_info": {
            "calories_per_100g": 265,
            "protein_per_100g": 18.3,
            "carbs_per_100g": 1.2,
            "fat_per_100g": 20.8,
            "fiber_per_100g": 0
        }
    },
    {
        "name": "Chicken Curry",
        "category": "meat",
        "region": "all",
        "nutritional_info": {
            "calories_per_100g": 180,
            "protein_per_100g": 25.0,
            "carbs_per_100g": 3.0,
            "fat_per_100g": 7.5,
            "fiber_per_100g": 0.5
        }
    },
    {
        "name": "Roti/Chapati",
        "category": "grain",
        "region": "north",
        "nutritional_info": {
            "calories_per_100g": 297,
            "protein_per_100g": 11.0,
            "carbs_per_100g": 58.6,
            "fat_per_100g": 4.4,
            "fiber_per_100g": 11.5
        }
    },
    {
        "name": "Idli",
        "category": "breakfast",
        "region": "south",
        "nutritional_info": {
            "calories_per_100g": 146,
            "protein_per_100g": 4.2,
            "carbs_per_100g": 28.8,
            "fat_per_100g": 1.0,
            "fiber_per_100g": 1.0
        }
    },
    {
        "name": "Samosa",
        "category": "snack",
        "region": "north",
        "nutritional_info": {
            "calories_per_100g": 308,
            "protein_per_100g": 5.4,
            "carbs_per_100g": 30.0,
            "fat_per_100g": 19.0,
            "fiber_per_100g": 3.0
        }
    },
    {
        "name": "Curd/Yogurt",
        "category": "dairy",
        "region": "all",
        "nutritional_info": {
            "calories_per_100g": 60,
            "protein_per_100g": 3.5,
            "carbs_per_100g": 4.7,
            "fat_per_100g": 3.3,
            "fiber_per_100g": 0
        }
    }
]

# Utility Functions
async def analyze_food_with_gemini(image_base64: str, description: str = "") -> Dict[str, Any]:
    """Analyze food image using Gemini AI"""
    try:
        # Use emergent integration for Gemini
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY', ''),
            session_id=f"food_analysis_{uuid.uuid4()}",
            system_message="You are a nutritionist AI specialized in Indian cuisine. Analyze food images and provide detailed nutritional information."
        ).with_model("gemini", "gemini-2.0-flash")

        # Create image content
        image_content = ImageContent(image_base64=image_base64)
        
        prompt = f"""
        Analyze this food image carefully and provide a detailed analysis:
        
        IMPORTANT INSTRUCTIONS:
        1. First, determine if this is Indian food or cuisine
        2. If it's NOT Indian food, respond with "NOT_INDIAN_FOOD" and stop analysis
        3. If it IS Indian food, provide detailed nutritional analysis
        
        For INDIAN FOOD only, analyze:
        - Identify specific Indian dishes (dal, rice, roti, sabzi, etc.)
        - Estimate realistic portion size in grams based on image
        - Provide accurate nutritional values based on the specific Indian foods identified
        - Give confidence level of your analysis (1-10)
        
        Additional context: {description}
        
        Format your response clearly:
        - If NOT Indian food: Just write "NOT_INDIAN_FOOD - This appears to be [food type] which is not Indian cuisine"
        - If Indian food: Provide detailed analysis of the specific dishes, realistic portion size, and accurate nutrition facts
        
        Be very accurate with portion sizes and nutrition - don't guess wildly.
        """

        user_message = UserMessage(
            text=prompt,
            file_contents=[image_content]
        )

        response = await chat.send_message(user_message)
        
        # Parse the response (assuming it returns JSON-like format)
        return {
            "analysis": response,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error analyzing food with Gemini: {str(e)}")
        return {
            "analysis": f"Error analyzing image: {str(e)}",
            "success": False
        }

def find_similar_food(food_name: str) -> Optional[dict]:
    """Find similar food in our database"""
    food_name_lower = food_name.lower()
    
    for food in indian_foods_db:
        if food_name_lower in food["name"].lower() or food["name"].lower() in food_name_lower:
            return food
    
    # If no exact match, return a default rice entry
    return indian_foods_db[0]  # Default to rice

def calculate_nutrition(food_data: dict, quantity_grams: float) -> Dict[str, float]:
    """Calculate nutrition based on quantity"""
    nutrition = food_data["nutritional_info"]
    factor = quantity_grams / 100.0
    
    return {
        "calories": nutrition["calories_per_100g"] * factor,
        "protein": nutrition["protein_per_100g"] * factor,
        "carbs": nutrition["carbs_per_100g"] * factor,
        "fat": nutrition["fat_per_100g"] * factor,
        "fiber": nutrition["fiber_per_100g"] * factor
    }

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "Indian Calorie Tracker API", "version": "1.0"}

@api_router.post("/analyze-meal", response_model=dict)
async def analyze_meal(request: MealAnalysisRequest):
    """Analyze meal from image using AI"""
    try:
        # Analyze with Gemini
        ai_result = await analyze_food_with_gemini(
            request.image_base64, 
            request.description or ""
        )
        
        if not ai_result["success"]:
            # Fallback - return empty values since we can't analyze properly
            return {
                "food_name": "Unable to analyze image",
                "estimated_quantity": None,
                "nutrition": {
                    "calories": None,
                    "protein": None,
                    "carbs": None,
                    "fat": None,
                    "fiber": None
                },
                "ai_analysis": "Could not analyze the image. Please try again with a clearer photo.",
                "confidence": 1,
                "is_indian_food": False
            }
        
        # Parse AI response and extract meaningful information
        analysis_text = ai_result["analysis"]
        
        # Check if it's not Indian food
        if "NOT_INDIAN_FOOD" in analysis_text.upper():
            return {
                "food_name": "Non-Indian Food Detected",
                "estimated_quantity": None,
                "nutrition": {
                    "calories": None,
                    "protein": None,
                    "carbs": None,
                    "fat": None,
                    "fiber": None
                },
                "ai_analysis": analysis_text,
                "confidence": 1,
                "is_indian_food": False
            }
        
        # Extract meaningful information from AI analysis for Indian food
        food_name = "Indian meal"
        estimated_quantity = 150.0  # Default reasonable portion
        
        # Try to extract more specific food identification
        analysis_lower = analysis_text.lower()
        
        # Identify specific Indian dishes
        if any(word in analysis_lower for word in ["rice", "biryani", "pulao"]):
            food_name = "Rice-based Indian dish"
            estimated_quantity = 200.0
        elif any(word in analysis_lower for word in ["dal", "lentil", "sambar", "rasam"]):
            food_name = "Dal/Lentil curry"
            estimated_quantity = 150.0
        elif any(word in analysis_lower for word in ["roti", "chapati", "naan", "paratha"]):
            food_name = "Indian bread"
            estimated_quantity = 80.0
        elif any(word in analysis_lower for word in ["curry", "sabzi", "vegetable"]):
            food_name = "Indian vegetable curry"
            estimated_quantity = 120.0
        elif any(word in analysis_lower for word in ["chicken", "mutton", "meat"]):
            food_name = "Indian meat curry"
            estimated_quantity = 150.0
        elif any(word in analysis_lower for word in ["paneer"]):
            food_name = "Paneer dish"
            estimated_quantity = 130.0
        elif any(word in analysis_lower for word in ["idli", "dosa", "uttapam"]):
            food_name = "South Indian breakfast"
            estimated_quantity = 120.0
        elif any(word in analysis_lower for word in ["samosa", "pakoda", "chaat"]):
            food_name = "Indian snack"
            estimated_quantity = 100.0
        
        # Find similar food in database for more accurate nutrition
        similar_food = find_similar_food(food_name)
        
        # Calculate realistic nutrition based on identified food type
        if similar_food:
            nutrition = calculate_nutrition(similar_food, estimated_quantity)
        else:
            # Provide reasonable estimates for mixed Indian meals
            base_calories_per_gram = 1.5  # Reasonable for Indian food
            nutrition = {
                "calories": round(estimated_quantity * base_calories_per_gram, 1),
                "protein": round(estimated_quantity * 0.06, 1),  # 6% protein
                "carbs": round(estimated_quantity * 0.25, 1),   # 25% carbs  
                "fat": round(estimated_quantity * 0.04, 1),     # 4% fat
                "fiber": round(estimated_quantity * 0.02, 1)    # 2% fiber
            }
        
        return {
            "food_name": food_name,
            "estimated_quantity": estimated_quantity,
            "nutrition": nutrition,
            "ai_analysis": analysis_text,
            "confidence": 8,
            "is_indian_food": True
        }
        
    except Exception as e:
        logger.error(f"Error in meal analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@api_router.post("/log-meal", response_model=dict)
async def log_meal(meal_data: dict):
    """Log a meal entry"""
    try:
        # Create meal entry
        meal_entry = {
            "_id": ObjectId(),
            "user_id": meal_data.get("user_id", "default_user"),
            "food_name": meal_data["food_name"],
            "estimated_quantity": meal_data["estimated_quantity"],
            "calories": meal_data["nutrition"]["calories"],
            "protein": meal_data["nutrition"]["protein"],
            "carbs": meal_data["nutrition"]["carbs"],
            "fat": meal_data["nutrition"]["fat"],
            "fiber": meal_data["nutrition"]["fiber"],
            "image_base64": meal_data.get("image_base64"),
            "ai_analysis": meal_data.get("ai_analysis"),
            "timestamp": datetime.utcnow(),
            "meal_type": meal_data.get("meal_type", "general")
        }
        
        # Insert into database
        result = await db.meals.insert_one(meal_entry)
        
        # Clean up old meals (keep only last 14)
        await cleanup_old_meals(meal_entry["user_id"])
        
        return {
            "success": True,
            "meal_id": str(result.inserted_id),
            "message": "Meal logged successfully"
        }
        
    except Exception as e:
        logger.error(f"Error logging meal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to log meal: {str(e)}")

@api_router.get("/meals/recent/{user_id}")
async def get_recent_meals(user_id: str = "default_user", limit: int = 14):
    """Get recent meals for user"""
    try:
        cursor = db.meals.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        meals = []
        async for meal in cursor:
            meal["_id"] = str(meal["_id"])
            meals.append(meal)
        
        return {
            "meals": meals,
            "total": len(meals)
        }
        
    except Exception as e:
        logger.error(f"Error fetching meals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch meals: {str(e)}")

@api_router.get("/nutrition/summary/{user_id}")
async def get_nutrition_summary(user_id: str = "default_user", days: int = 1):
    """Get nutrition summary for specified days"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        cursor = db.meals.find({
            "user_id": user_id,
            "timestamp": {"$gte": start_date}
        })
        
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_fiber = 0
        meal_count = 0
        
        async for meal in cursor:
            total_calories += meal.get("calories", 0)
            total_protein += meal.get("protein", 0)
            total_carbs += meal.get("carbs", 0)
            total_fat += meal.get("fat", 0)
            total_fiber += meal.get("fiber", 0)
            meal_count += 1
        
        return {
            "period_days": days,
            "total_meals": meal_count,
            "total_calories": round(total_calories, 2),
            "total_protein": round(total_protein, 2),
            "total_carbs": round(total_carbs, 2),
            "total_fat": round(total_fat, 2),
            "total_fiber": round(total_fiber, 2),
            "daily_average": {
                "calories": round(total_calories / days, 2),
                "protein": round(total_protein / days, 2),
                "carbs": round(total_carbs / days, 2),
                "fat": round(total_fat / days, 2),
                "fiber": round(total_fiber / days, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting nutrition summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/protein-recommendations/{user_id}")
async def get_protein_recommendations(user_id: str = "default_user"):
    """Get personalized protein recommendations"""
    try:
        # Get today's protein intake
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        cursor = db.meals.find({
            "user_id": user_id,
            "timestamp": {"$gte": today_start}
        })
        
        current_protein = 0
        async for meal in cursor:
            current_protein += meal.get("protein", 0)
        
        # Recommended daily protein (0.8g per kg body weight, assuming 70kg person)
        recommended_daily = 56.0  # Can be made dynamic based on user profile
        deficit = max(0, recommended_daily - current_protein)
        
        high_protein_foods = [
            "Paneer (18g protein per 100g)",
            "Dal/Lentils (22g protein per 100g)",
            "Chicken (25g protein per 100g)",
            "Chickpeas (19g protein per 100g)",
            "Greek Yogurt (10g protein per 100g)"
        ]
        
        meal_suggestions = []
        if deficit > 20:
            meal_suggestions = [
                "Add a bowl of dal or lentils (15-20g protein)",
                "Include paneer in your next meal (15-18g protein)",
                "Have a protein smoothie with yogurt and nuts"
            ]
        elif deficit > 10:
            meal_suggestions = [
                "Add some nuts or seeds to your meal",
                "Include a small portion of paneer or dal",
                "Have a glass of buttermilk or lassi"
            ]
        elif deficit > 0:
            meal_suggestions = [
                "You're close to your target! Add some nuts as snack",
                "A small bowl of yogurt will complete your protein needs"
            ]
        else:
            meal_suggestions = [
                "Great job! You've met your protein target for today",
                "Maintain this balanced approach to nutrition"
            ]
        
        return {
            "recommended_daily_protein": recommended_daily,
            "current_protein": round(current_protein, 2),
            "deficit": round(deficit, 2),
            "percentage_complete": round((current_protein / recommended_daily) * 100, 1),
            "high_protein_foods": high_protein_foods,
            "meal_suggestions": meal_suggestions
        }
        
    except Exception as e:
        logger.error(f"Error getting protein recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/meals/{meal_id}")
async def delete_meal(meal_id: str):
    """Delete a specific meal by ID"""
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(meal_id)
        
        # Delete the meal
        result = await db.meals.delete_one({"_id": object_id})
        
        if result.deleted_count == 1:
            return {
                "success": True,
                "message": "Meal deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Meal not found")
            
    except Exception as e:
        logger.error(f"Error deleting meal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete meal: {str(e)}")

@api_router.get("/foods/search")
async def search_indian_foods(query: str = ""):
    """Search Indian foods database"""
    try:
        if not query:
            return {"foods": indian_foods_db[:10]}
        
        query_lower = query.lower()
        matching_foods = []
        
        for food in indian_foods_db:
            if (query_lower in food["name"].lower() or 
                query_lower in food["category"].lower() or
                query_lower in food["region"].lower()):
                matching_foods.append(food)
        
        return {"foods": matching_foods}
        
    except Exception as e:
        logger.error(f"Error searching foods: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def cleanup_old_meals(user_id: str):
    """Keep only the most recent 14 meals"""
    try:
        # Get all meals for user, sorted by timestamp descending
        cursor = db.meals.find({"user_id": user_id}).sort("timestamp", -1)
        
        meals = []
        async for meal in cursor:
            meals.append(meal)
        
        # If more than 14 meals, delete the oldest ones
        if len(meals) > 14:
            meals_to_delete = meals[14:]  # Keep first 14, delete rest
            meal_ids = [meal["_id"] for meal in meals_to_delete]
            
            await db.meals.delete_many({"_id": {"$in": meal_ids}})
            logger.info(f"Cleaned up {len(meal_ids)} old meals for user {user_id}")
            
    except Exception as e:
        logger.error(f"Error cleaning up old meals: {str(e)}")

# Include router in app
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)