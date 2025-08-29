#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Indian Calorie Tracker API
Tests all backend endpoints with realistic Indian food data
"""

import requests
import json
import base64
import io
from PIL import Image
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://protein-pulse-india.preview.emergentagent.com/api"

def create_sample_food_image():
    """Create a sample food image as base64 for testing"""
    # Create a simple colored image representing food
    img = Image.new('RGB', (300, 300), color='orange')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    img_data = buffer.getvalue()
    return base64.b64encode(img_data).decode('utf-8')

def test_health_endpoint():
    """Test the basic health check endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "Indian Calorie Tracker API" in data["message"]:
                print("✅ Health endpoint working correctly")
                return True
            else:
                print("❌ Health endpoint response format incorrect")
                return False
        else:
            print(f"❌ Health endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint error: {str(e)}")
        return False

def test_analyze_meal_endpoint():
    """Test the meal analysis endpoint with AI"""
    print("\n=== Testing Analyze Meal Endpoint ===")
    try:
        # Create sample image
        sample_image = create_sample_food_image()
        
        payload = {
            "image_base64": sample_image,
            "description": "A plate of dal rice with vegetables"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/analyze-meal",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check required fields
            required_fields = ["food_name", "estimated_quantity", "nutrition", "ai_analysis"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                nutrition = data["nutrition"]
                nutrition_fields = ["calories", "protein", "carbs", "fat", "fiber"]
                missing_nutrition = [field for field in nutrition_fields if field not in nutrition]
                
                if not missing_nutrition:
                    print("✅ Analyze meal endpoint working correctly")
                    return True, data
                else:
                    print(f"❌ Missing nutrition fields: {missing_nutrition}")
                    return False, None
            else:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
        else:
            print(f"❌ Analyze meal failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Analyze meal error: {str(e)}")
        return False, None

def test_log_meal_endpoint(meal_data=None):
    """Test the meal logging endpoint"""
    print("\n=== Testing Log Meal Endpoint ===")
    try:
        if not meal_data:
            # Create sample meal data
            meal_data = {
                "user_id": "test_user_raj",
                "food_name": "Dal Rice with Sabzi",
                "estimated_quantity": 250.0,
                "nutrition": {
                    "calories": 320.5,
                    "protein": 12.8,
                    "carbs": 58.2,
                    "fat": 4.5,
                    "fiber": 6.2
                },
                "image_base64": create_sample_food_image(),
                "ai_analysis": "Test meal logging with dal rice",
                "meal_type": "lunch"
            }
        
        response = requests.post(
            f"{BACKEND_URL}/log-meal",
            json=meal_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get("success") and "meal_id" in data:
                print("✅ Log meal endpoint working correctly")
                return True, data["meal_id"]
            else:
                print("❌ Log meal response format incorrect")
                return False, None
        else:
            print(f"❌ Log meal failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Log meal error: {str(e)}")
        return False, None

def test_recent_meals_endpoint(user_id="test_user_raj"):
    """Test the recent meals retrieval endpoint"""
    print("\n=== Testing Recent Meals Endpoint ===")
    try:
        response = requests.get(f"{BACKEND_URL}/meals/recent/{user_id}")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if "meals" in data and "total" in data:
                print(f"✅ Recent meals endpoint working correctly - Found {data['total']} meals")
                return True, data["meals"]
            else:
                print("❌ Recent meals response format incorrect")
                return False, None
        else:
            print(f"❌ Recent meals failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Recent meals error: {str(e)}")
        return False, None

def test_nutrition_summary_endpoint(user_id="test_user_raj", days=1):
    """Test the nutrition summary endpoint"""
    print("\n=== Testing Nutrition Summary Endpoint ===")
    try:
        response = requests.get(f"{BACKEND_URL}/nutrition/summary/{user_id}?days={days}")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            required_fields = ["period_days", "total_meals", "total_calories", "total_protein", "daily_average"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                daily_avg = data["daily_average"]
                avg_fields = ["calories", "protein", "carbs", "fat", "fiber"]
                missing_avg = [field for field in avg_fields if field not in daily_avg]
                
                if not missing_avg:
                    print("✅ Nutrition summary endpoint working correctly")
                    return True, data
                else:
                    print(f"❌ Missing daily average fields: {missing_avg}")
                    return False, None
            else:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
        else:
            print(f"❌ Nutrition summary failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Nutrition summary error: {str(e)}")
        return False, None

def test_protein_recommendations_endpoint(user_id="test_user_raj"):
    """Test the protein recommendations endpoint"""
    print("\n=== Testing Protein Recommendations Endpoint ===")
    try:
        response = requests.get(f"{BACKEND_URL}/protein-recommendations/{user_id}")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            required_fields = ["recommended_daily_protein", "current_protein", "deficit", "high_protein_foods", "meal_suggestions"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                if isinstance(data["high_protein_foods"], list) and isinstance(data["meal_suggestions"], list):
                    print("✅ Protein recommendations endpoint working correctly")
                    return True, data
                else:
                    print("❌ Protein recommendations lists format incorrect")
                    return False, None
            else:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
        else:
            print(f"❌ Protein recommendations failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Protein recommendations error: {str(e)}")
        return False, None

def test_foods_search_endpoint():
    """Test the Indian foods search endpoint"""
    print("\n=== Testing Foods Search Endpoint ===")
    try:
        # Test without query (should return default foods)
        response = requests.get(f"{BACKEND_URL}/foods/search")
        
        print(f"Status Code (no query): {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response (no query): Found {len(data.get('foods', []))} foods")
            
            if "foods" in data and isinstance(data["foods"], list):
                # Test with specific query
                response2 = requests.get(f"{BACKEND_URL}/foods/search?query=dal")
                
                print(f"Status Code (dal query): {response2.status_code}")
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    print(f"Response (dal query): Found {len(data2.get('foods', []))} foods")
                    
                    # Test with rice query
                    response3 = requests.get(f"{BACKEND_URL}/foods/search?query=rice")
                    
                    if response3.status_code == 200:
                        data3 = response3.json()
                        print(f"Response (rice query): Found {len(data3.get('foods', []))} foods")
                        print("✅ Foods search endpoint working correctly")
                        return True, data
                    else:
                        print(f"❌ Rice query failed with status {response3.status_code}")
                        return False, None
                else:
                    print(f"❌ Dal query failed with status {response2.status_code}")
                    return False, None
            else:
                print("❌ Foods search response format incorrect")
                return False, None
        else:
            print(f"❌ Foods search failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Foods search error: {str(e)}")
        return False, None

def test_meal_cleanup_functionality():
    """Test that meal cleanup works (keeps only 14 meals)"""
    print("\n=== Testing Meal Cleanup Functionality ===")
    try:
        user_id = "cleanup_test_user"
        
        # Log 16 meals to test cleanup
        print("Logging 16 meals to test cleanup...")
        for i in range(16):
            meal_data = {
                "user_id": user_id,
                "food_name": f"Test Meal {i+1}",
                "estimated_quantity": 200.0,
                "nutrition": {
                    "calories": 250 + i,
                    "protein": 10 + i,
                    "carbs": 40 + i,
                    "fat": 5 + i,
                    "fiber": 3 + i
                },
                "meal_type": "test"
            }
            
            success, meal_id = test_log_meal_endpoint(meal_data)
            if not success:
                print(f"❌ Failed to log meal {i+1}")
                return False
            
            time.sleep(0.1)  # Small delay to ensure different timestamps
        
        # Check that only 14 meals remain
        success, meals = test_recent_meals_endpoint(user_id)
        if success:
            if len(meals) <= 14:
                print(f"✅ Meal cleanup working correctly - {len(meals)} meals retained")
                return True
            else:
                print(f"❌ Meal cleanup failed - {len(meals)} meals found (should be ≤14)")
                return False
        else:
            print("❌ Could not verify meal cleanup")
            return False
            
    except Exception as e:
        print(f"❌ Meal cleanup test error: {str(e)}")
        return False

def run_comprehensive_backend_tests():
    """Run all backend tests in sequence"""
    print("🚀 Starting Comprehensive Backend Testing for Indian Calorie Tracker")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    test_results = {}
    
    # Test 1: Health Check
    test_results["health"] = test_health_endpoint()
    
    # Test 2: Analyze Meal
    success, meal_analysis = test_analyze_meal_endpoint()
    test_results["analyze_meal"] = success
    
    # Test 3: Log Meal (use analysis data if available)
    if success and meal_analysis:
        # Use the analyzed meal data for logging
        meal_data = {
            "user_id": "test_user_priya",
            "food_name": meal_analysis["food_name"],
            "estimated_quantity": meal_analysis["estimated_quantity"],
            "nutrition": meal_analysis["nutrition"],
            "image_base64": create_sample_food_image(),
            "ai_analysis": meal_analysis["ai_analysis"],
            "meal_type": "dinner"
        }
        success, meal_id = test_log_meal_endpoint(meal_data)
        test_results["log_meal"] = success
    else:
        success, meal_id = test_log_meal_endpoint()
        test_results["log_meal"] = success
    
    # Test 4: Recent Meals
    test_results["recent_meals"] = test_recent_meals_endpoint("test_user_priya")[0]
    
    # Test 5: Nutrition Summary
    test_results["nutrition_summary"] = test_nutrition_summary_endpoint("test_user_priya")[0]
    
    # Test 6: Protein Recommendations
    test_results["protein_recommendations"] = test_protein_recommendations_endpoint("test_user_priya")[0]
    
    # Test 7: Foods Search
    test_results["foods_search"] = test_foods_search_endpoint()[0]
    
    # Test 8: Meal Cleanup
    test_results["meal_cleanup"] = test_meal_cleanup_functionality()
    
    # Summary
    print("\n" + "=" * 80)
    print("🏁 BACKEND TESTING SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All backend tests PASSED! The Indian Calorie Tracker API is working correctly.")
    else:
        print(f"⚠️  {total - passed} test(s) FAILED. Please check the issues above.")
    
    return test_results

if __name__ == "__main__":
    results = run_comprehensive_backend_tests()