import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
  RefreshControl,
  SafeAreaView,
  Modal,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import Constants from 'expo-constants';

const API_BASE_URL = Constants.expoConfig?.extra?.EXPO_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

interface NutritionData {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
}

interface MealEntry {
  _id: string;
  food_name: string;
  estimated_quantity: number;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  timestamp: string;
  image_base64?: string;
  ai_analysis?: string;
}

interface ProteinRecommendation {
  recommended_daily_protein: number;
  current_protein: number;
  deficit: number;
  percentage_complete: number;
  high_protein_foods: string[];
  meal_suggestions: string[];
}

export default function CalorieTracker() {
  const [currentView, setCurrentView] = useState<'camera' | 'history' | 'recommendations'>('camera');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [recentMeals, setRecentMeals] = useState<MealEntry[]>([]);
  const [todaysNutrition, setTodaysNutrition] = useState<NutritionData>({ calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0 });
  const [proteinRec, setProteinRec] = useState<ProteinRecommendation | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [lastAnalyzedMeal, setLastAnalyzedMeal] = useState<any>(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState<string | null>(null);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [deletingMealId, setDeletingMealId] = useState<string | null>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    await Promise.all([
      fetchRecentMeals(),
      fetchTodaysNutrition(),
      fetchProteinRecommendations()
    ]);
  };

  const fetchRecentMeals = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/meals/recent/default_user`);
      const data = await response.json();
      setRecentMeals(data.meals || []);
    } catch (error) {
      console.error('Error fetching meals:', error);
    }
  };

  const fetchTodaysNutrition = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/nutrition/summary/default_user?days=1`);
      const data = await response.json();
      setTodaysNutrition({
        calories: data.total_calories || 0,
        protein: data.total_protein || 0,
        carbs: data.total_carbs || 0,
        fat: data.total_fat || 0,
        fiber: data.total_fiber || 0,
      });
    } catch (error) {
      console.error('Error fetching nutrition:', error);
    }
  };

  const fetchProteinRecommendations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/protein-recommendations/default_user`);
      const data = await response.json();
      setProteinRec(data);
    } catch (error) {
      console.error('Error fetching protein recommendations:', error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadInitialData();
    setRefreshing(false);
  };

  const pickImageFromCamera = async () => {
    try {
      const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
      
      if (permissionResult.granted === false) {
        Alert.alert('Permission Required', 'Camera permission is required to scan food');
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.7,
        base64: true,
      });

      if (!result.canceled && result.assets[0].base64) {
        await analyzeFoodImage(result.assets[0].base64);
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Error', 'Failed to capture image');
    }
  };

  const pickImageFromLibrary = async () => {
    try {
      const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
      
      if (permissionResult.granted === false) {
        Alert.alert('Permission Required', 'Photo library permission is required');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.7,
        base64: true,
      });

      if (!result.canceled && result.assets[0].base64) {
        await analyzeFoodImage(result.assets[0].base64);
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Error', 'Failed to select image');
    }
  };

  const analyzeFoodImage = async (base64Image: string) => {
    setIsAnalyzing(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze-meal`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_base64: base64Image,
          description: 'Indian food meal analysis'
        }),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const analysisResult = await response.json();
      
      setLastAnalyzedMeal({
        ...analysisResult,
        image_base64: base64Image
      });

      // Show confirmation dialog
      Alert.alert(
        'Meal Analysis Complete',
        analysisResult.estimated_quantity && analysisResult.nutrition.calories ? 
          `Food: ${analysisResult.food_name}\nEstimated: ${analysisResult.estimated_quantity}g\nCalories: ${Math.round(analysisResult.nutrition.calories)}\nProtein: ${Math.round(analysisResult.nutrition.protein)}g\n\nDo you want to log this meal?` :
          `Analysis: ${analysisResult.food_name}\n\n${analysisResult.ai_analysis}\n\nDo you want to log this entry?`,
        [
          { text: 'Cancel', style: 'cancel' },
          { 
            text: 'Log Meal', 
            onPress: () => logAnalyzedMeal(analysisResult, base64Image)
          }
        ]
      );

    } catch (error) {
      console.error('Error analyzing food:', error);
      Alert.alert('Error', 'Failed to analyze food image. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const logAnalyzedMeal = async (analysisResult: any, imageBase64: string) => {
    try {
      const mealData = {
        user_id: 'default_user',
        food_name: analysisResult.food_name,
        estimated_quantity: analysisResult.estimated_quantity,
        nutrition: analysisResult.nutrition,
        image_base64: imageBase64,
        ai_analysis: analysisResult.ai_analysis,
        meal_type: 'general'
      };

      const response = await fetch(`${API_BASE_URL}/api/log-meal`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mealData),
      });

      if (response.ok) {
        Alert.alert('Success', 'Meal logged successfully!');
        await loadInitialData(); // Refresh all data
      } else {
        throw new Error('Failed to log meal');
      }
      
    } catch (error) {
      console.error('Error logging meal:', error);
      Alert.alert('Error', 'Failed to log meal');
    }
  };

  const deleteMeal = async (mealId: string) => {
    Alert.alert(
      'Delete Meal',
      'Are you sure you want to delete this meal? This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive',
          onPress: async () => {
            try {
              setDeletingMealId(mealId);
              
              const response = await fetch(`${API_BASE_URL}/api/meals/${mealId}`, {
                method: 'DELETE',
              });

              if (response.ok) {
                Alert.alert('Success', 'Meal deleted successfully!');
                await loadInitialData(); // Refresh all data
              } else {
                throw new Error('Failed to delete meal');
              }
              
            } catch (error) {
              console.error('Error deleting meal:', error);
              Alert.alert('Error', 'Failed to delete meal');
            } finally {
              setDeletingMealId(null);
            }
          }
        }
      ]
    );
  };

  const showFullAnalysis = (analysis: string) => {
    const cleanAnalysis = typeof analysis === 'string' 
      ? analysis.replace(/[{}"\[\]]/g, '').replace(/,/g, ', ')
      : JSON.stringify(analysis).replace(/[{}"\[\]]/g, '').replace(/,/g, ', ');
    
    setSelectedAnalysis(cleanAnalysis);
    setShowAnalysisModal(true);
  };

  const renderCameraView = () => (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Calorie Tracker</Text>
        <Text style={styles.headerSubtitle}>Scan Indian food & track nutrition</Text>
      </View>

      {/* Today's Summary */}
      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>Today's Nutrition</Text>
        <View style={styles.nutritionGrid}>
          <View style={styles.nutritionItem}>
            <Text style={styles.nutritionValue}>{Math.round(todaysNutrition.calories)}</Text>
            <Text style={styles.nutritionLabel}>Calories</Text>
          </View>
          <View style={styles.nutritionItem}>
            <Text style={styles.nutritionValue}>{Math.round(todaysNutrition.protein)}g</Text>
            <Text style={styles.nutritionLabel}>Protein</Text>
          </View>
          <View style={styles.nutritionItem}>
            <Text style={styles.nutritionValue}>{Math.round(todaysNutrition.carbs)}g</Text>
            <Text style={styles.nutritionLabel}>Carbs</Text>
          </View>
          <View style={styles.nutritionItem}>
            <Text style={styles.nutritionValue}>{Math.round(todaysNutrition.fat)}g</Text>
            <Text style={styles.nutritionLabel}>Fat</Text>
          </View>
        </View>
      </View>

      {/* Camera Actions */}
      <View style={styles.actionCard}>
        <Text style={styles.actionTitle}>Scan Your Meal</Text>
        <Text style={styles.actionSubtitle}>Take a photo or select from gallery to analyze</Text>
        
        <View style={styles.buttonRow}>
          <TouchableOpacity 
            style={[styles.actionButton, styles.cameraButton]} 
            onPress={pickImageFromCamera}
            disabled={isAnalyzing}
          >
            <Ionicons name="camera" size={24} color="white" />
            <Text style={styles.buttonText}>Take Photo</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.actionButton, styles.galleryButton]} 
            onPress={pickImageFromLibrary}
            disabled={isAnalyzing}
          >
            <Ionicons name="images" size={24} color="white" />
            <Text style={styles.buttonText}>Gallery</Text>
          </TouchableOpacity>
        </View>

        {isAnalyzing && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#FF6B6B" />
            <Text style={styles.loadingText}>Analyzing your meal...</Text>
          </View>
        )}
      </View>

      {/* Recent Meals Preview */}
      {recentMeals.length > 0 && (
        <View style={styles.previewCard}>
          <Text style={styles.previewTitle}>Recent Meals</Text>
          {recentMeals.slice(0, 3).map((meal) => (
            <View key={meal._id} style={styles.previewMeal}>
              <View style={styles.mealInfo}>
                <Text style={styles.mealName}>{meal.food_name}</Text>
                <Text style={styles.mealDetails}>
                  {Math.round(meal.calories)} cal • {Math.round(meal.protein)}g protein
                </Text>
              </View>
              {meal.image_base64 && (
                <Image 
                  source={{ uri: `data:image/jpeg;base64,${meal.image_base64}` }}
                  style={styles.mealThumbnail}
                />
              )}
            </View>
          ))}
          <TouchableOpacity 
            style={styles.viewAllButton}
            onPress={() => setCurrentView('history')}
          >
            <Text style={styles.viewAllText}>View All Meals</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );

  const renderHistoryView = () => (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Meal History</Text>
        <Text style={styles.headerSubtitle}>Last 14 meals tracked</Text>
      </View>

      {recentMeals.map((meal) => (
        <View key={meal._id} style={styles.mealCard}>
          <View style={styles.mealHeader}>
            <View style={styles.mealHeaderLeft}>
              <Text style={styles.mealName}>{meal.food_name}</Text>
              <Text style={styles.mealDate}>
                {new Date(meal.timestamp).toLocaleDateString()} at{' '}
                {new Date(meal.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </Text>
            </View>
            <View style={styles.mealHeaderRight}>
              {meal.image_base64 && (
                <Image 
                  source={{ uri: `data:image/jpeg;base64,${meal.image_base64}` }}
                  style={styles.mealImage}
                />
              )}
              <TouchableOpacity 
                style={styles.deleteButton}
                onPress={() => deleteMeal(meal._id)}
                disabled={deletingMealId === meal._id}
              >
                {deletingMealId === meal._id ? (
                  <ActivityIndicator size="small" color="#e74c3c" />
                ) : (
                  <Ionicons name="trash" size={20} color="#e74c3c" />
                )}
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.mealNutrition}>
            {meal.estimated_quantity && meal.calories ? (
              <>
                <View style={styles.nutritionRow}>
                  <Text style={styles.nutritionText}>Quantity: {Math.round(meal.estimated_quantity)}g</Text>
                  <Text style={styles.nutritionText}>{Math.round(meal.calories)} calories</Text>
                </View>
                <View style={styles.nutritionRow}>
                  <Text style={styles.nutritionText}>Protein: {Math.round(meal.protein)}g</Text>
                  <Text style={styles.nutritionText}>Carbs: {Math.round(meal.carbs)}g</Text>
                </View>
                <Text style={styles.nutritionText}>Fat: {Math.round(meal.fat)}g • Fiber: {Math.round(meal.fiber)}g</Text>
              </>
            ) : (
              <View style={styles.noNutritionData}>
                <Ionicons name="information-circle" size={16} color="#95a5a6" />
                <Text style={styles.noNutritionText}>
                  {meal.food_name.includes('Non-Indian') || meal.food_name.includes('Unable to analyze') 
                    ? "Nutritional data not available for this food item"
                    : "Analysis in progress - nutritional data pending"
                  }
                </Text>
              </View>
            )}
          </View>

          {meal.ai_analysis && (
            <TouchableOpacity 
              style={styles.aiAnalysis}
              onPress={() => showFullAnalysis(meal.ai_analysis)}
            >
              <View style={styles.aiAnalysisHeader}>
                <Text style={styles.aiAnalysisTitle}>AI Analysis:</Text>
                <Ionicons name="expand" size={16} color="#7f8c8d" />
              </View>
              <Text style={styles.aiAnalysisText} numberOfLines={3}>
                {typeof meal.ai_analysis === 'string' 
                  ? meal.ai_analysis.replace(/[{}"\[\]]/g, '').replace(/,/g, ', ')
                  : JSON.stringify(meal.ai_analysis).replace(/[{}"\[\]]/g, '').replace(/,/g, ', ')
                }
              </Text>
              <Text style={styles.tapToExpand}>Tap to see full analysis</Text>
            </TouchableOpacity>
          )}
        </View>
      ))}

      {recentMeals.length === 0 && (
        <View style={styles.emptyState}>
          <Ionicons name="restaurant" size={48} color="#ccc" />
          <Text style={styles.emptyText}>No meals logged yet</Text>
          <Text style={styles.emptySubtext}>Start by scanning your first meal!</Text>
        </View>
      )}
    </ScrollView>
  );

  const renderRecommendationsView = () => (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Protein Guide</Text>
        <Text style={styles.headerSubtitle}>Personalized recommendations</Text>
      </View>

      {proteinRec && (
        <>
          {/* Protein Progress */}
          <View style={styles.progressCard}>
            <Text style={styles.progressTitle}>Today's Protein Progress</Text>
            <View style={styles.progressBar}>
              <View 
                style={[
                  styles.progressFill, 
                  { width: `${Math.min(proteinRec.percentage_complete, 100)}%` }
                ]} 
              />
            </View>
            <View style={styles.progressStats}>
              <Text style={styles.progressText}>
                {Math.round(proteinRec.current_protein)}g / {proteinRec.recommended_daily_protein}g
              </Text>
              <Text style={styles.progressPercentage}>
                {Math.round(proteinRec.percentage_complete)}%
              </Text>
            </View>
            
            {proteinRec.deficit > 0 && (
              <Text style={styles.deficitText}>
                You need {Math.round(proteinRec.deficit)}g more protein today
              </Text>
            )}
          </View>

          {/* Meal Suggestions */}
          <View style={styles.suggestionCard}>
            <Text style={styles.suggestionTitle}>Recommended Actions</Text>
            {proteinRec.meal_suggestions.map((suggestion, index) => (
              <View key={index} style={styles.suggestionItem}>
                <Ionicons name="checkmark-circle" size={20} color="#4ECDC4" />
                <Text style={styles.suggestionText}>{suggestion}</Text>
              </View>
            ))}
          </View>

          {/* High Protein Foods */}
          <View style={styles.foodsCard}>
            <Text style={styles.foodsTitle}>High Protein Indian Foods</Text>
            {proteinRec.high_protein_foods.map((food, index) => (
              <View key={index} style={styles.foodItem}>
                <Ionicons name="nutrition" size={18} color="#FF6B6B" />
                <Text style={styles.foodText}>{food}</Text>
              </View>
            ))}
          </View>
        </>
      )}
    </ScrollView>
  );

  const renderBottomNavigation = () => (
    <View style={styles.bottomNav}>
      <TouchableOpacity 
        style={[styles.navButton, currentView === 'camera' && styles.activeNavButton]}
        onPress={() => setCurrentView('camera')}
      >
        <Ionicons 
          name="camera" 
          size={24} 
          color={currentView === 'camera' ? '#FF6B6B' : '#666'} 
        />
        <Text style={[styles.navText, currentView === 'camera' && styles.activeNavText]}>
          Scan
        </Text>
      </TouchableOpacity>

      <TouchableOpacity 
        style={[styles.navButton, currentView === 'history' && styles.activeNavButton]}
        onPress={() => setCurrentView('history')}
      >
        <Ionicons 
          name="time" 
          size={24} 
          color={currentView === 'history' ? '#FF6B6B' : '#666'} 
        />
        <Text style={[styles.navText, currentView === 'history' && styles.activeNavText]}>
          History
        </Text>
      </TouchableOpacity>

      <TouchableOpacity 
        style={[styles.navButton, currentView === 'recommendations' && styles.activeNavButton]}
        onPress={() => setCurrentView('recommendations')}
      >
        <Ionicons 
          name="fitness" 
          size={24} 
          color={currentView === 'recommendations' ? '#FF6B6B' : '#666'} 
        />
        <Text style={[styles.navText, currentView === 'recommendations' && styles.activeNavText]}>
          Protein
        </Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.mainContainer}>
        {currentView === 'camera' && renderCameraView()}
        {currentView === 'history' && renderHistoryView()}
        {currentView === 'recommendations' && renderRecommendationsView()}
        {renderBottomNavigation()}
        
        {/* AI Analysis Modal */}
        <Modal
          visible={showAnalysisModal}
          animationType="slide"
          presentationStyle="pageSheet"
        >
          <SafeAreaView style={styles.modalContainer}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Complete AI Analysis</Text>
              <TouchableOpacity 
                onPress={() => setShowAnalysisModal(false)}
                style={styles.closeButton}
              >
                <Ionicons name="close" size={24} color="#2c3e50" />
              </TouchableOpacity>
            </View>
            
            <ScrollView style={styles.modalContent}>
              <Text style={styles.fullAnalysisText}>
                {selectedAnalysis}
              </Text>
            </ScrollView>
          </SafeAreaView>
        </Modal>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  mainContainer: {
    flex: 1,
  },
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    padding: 20,
    paddingTop: 40,
    backgroundColor: 'white',
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#7f8c8d',
  },
  summaryCard: {
    margin: 16,
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  summaryTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 16,
  },
  nutritionGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  nutritionItem: {
    alignItems: 'center',
  },
  nutritionValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FF6B6B',
  },
  nutritionLabel: {
    fontSize: 12,
    color: '#7f8c8d',
    marginTop: 4,
  },
  actionCard: {
    margin: 16,
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  actionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 8,
  },
  actionSubtitle: {
    fontSize: 14,
    color: '#7f8c8d',
    marginBottom: 20,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 8,
    gap: 8,
  },
  cameraButton: {
    backgroundColor: '#FF6B6B',
  },
  galleryButton: {
    backgroundColor: '#4ECDC4',
  },
  buttonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 16,
  },
  loadingContainer: {
    alignItems: 'center',
    marginTop: 20,
  },
  loadingText: {
    marginTop: 8,
    color: '#7f8c8d',
  },
  previewCard: {
    margin: 16,
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  previewTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 16,
  },
  previewMeal: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  mealInfo: {
    flex: 1,
  },
  mealName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#2c3e50',
  },
  mealDetails: {
    fontSize: 14,
    color: '#7f8c8d',
    marginTop: 4,
  },
  mealThumbnail: {
    width: 40,
    height: 40,
    borderRadius: 8,
  },
  viewAllButton: {
    alignSelf: 'center',
    marginTop: 16,
    paddingHorizontal: 20,
    paddingVertical: 10,
    backgroundColor: '#ecf0f1',
    borderRadius: 20,
  },
  viewAllText: {
    color: '#FF6B6B',
    fontWeight: '500',
  },
  mealCard: {
    margin: 16,
    marginBottom: 8,
    padding: 16,
    backgroundColor: 'white',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  mealHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  mealHeaderLeft: {
    flex: 1,
    marginRight: 12,
  },
  mealHeaderRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  mealDate: {
    fontSize: 12,
    color: '#7f8c8d',
    marginTop: 4,
  },
  mealImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
  },
  deleteButton: {
    padding: 8,
    borderRadius: 20,
    backgroundColor: '#ffebee',
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 36,
    minHeight: 36,
  },
  mealNutrition: {
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#ecf0f1',
  },
  nutritionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  nutritionText: {
    fontSize: 14,
    color: '#2c3e50',
  },
  aiAnalysis: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  aiAnalysisHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  aiAnalysisTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#7f8c8d',
  },
  aiAnalysisText: {
    fontSize: 12,
    color: '#2c3e50',
    lineHeight: 16,
    marginBottom: 4,
  },
  tapToExpand: {
    fontSize: 10,
    color: '#95a5a6',
    fontStyle: 'italic',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
    marginTop: 60,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '500',
    color: '#7f8c8d',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#95a5a6',
    marginTop: 8,
    textAlign: 'center',
  },
  // Modal Styles
  modalContainer: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  closeButton: {
    padding: 8,
    borderRadius: 20,
    backgroundColor: '#f8f9fa',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  fullAnalysisText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#2c3e50',
  },
  // No nutrition data styles
  noNutritionData: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  noNutritionText: {
    fontSize: 14,
    color: '#6c757d',
    marginLeft: 8,
    flex: 1,
    fontStyle: 'italic',
  },
  progressCard: {
    margin: 16,
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  progressTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 16,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#ecf0f1',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 12,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4ECDC4',
  },
  progressStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  progressText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#2c3e50',
  },
  progressPercentage: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4ECDC4',
  },
  deficitText: {
    fontSize: 14,
    color: '#e74c3c',
    marginTop: 8,
    fontWeight: '500',
  },
  suggestionCard: {
    margin: 16,
    marginTop: 0,
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  suggestionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 16,
  },
  suggestionItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
    paddingRight: 16,
  },
  suggestionText: {
    fontSize: 14,
    color: '#2c3e50',
    marginLeft: 12,
    flex: 1,
    lineHeight: 20,
  },
  foodsCard: {
    margin: 16,
    marginTop: 0,
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  foodsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 16,
  },
  foodItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  foodText: {
    fontSize: 14,
    color: '#2c3e50',
    marginLeft: 12,
  },
  bottomNav: {
    flexDirection: 'row',
    backgroundColor: 'white',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderTopWidth: 1,
    borderTopColor: '#ecf0f1',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: -2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  navButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
  },
  activeNavButton: {
    backgroundColor: '#fff5f5',
    borderRadius: 12,
  },
  navText: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  activeNavText: {
    color: '#FF6B6B',
    fontWeight: '500',
  },
});