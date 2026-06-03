import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

print("Veri seti yükleniyor...")
df = pd.read_csv('data/recipes.csv')
df = df[['Name', 'RecipeIngredientParts', 'TotalTime', 'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent', 'RecipeInstructions']]
df = df.dropna(subset=['Name', 'RecipeIngredientParts']) 
if len(df) > 20000: df = df.sample(20000, random_state=42).reset_index(drop=True)
def get_image_for_recipe(recipe_name):
    text = str(recipe_name).lower()
    
    # KESİNLİKLE KIRILMAYAN STATİK GÖRSEL HAVUZU
    IMAGE_MAP = {
        # TAVUK VE KÜMES HAYVANLARI
        "chicken": "https://images.unsplash.com/photo-1598103444220-d326f55462cf?w=800",
        "turkey": "https://images.unsplash.com/photo-1598103444220-d326f55462cf?w=800",
        "duck": "https://images.unsplash.com/photo-1598103444220-d326f55462cf?w=800",
        "poultry": "https://images.unsplash.com/photo-1598103444220-d326f55462cf?w=800",
        
        # ET VE KEBAP
        "beef": "https://images.unsplash.com/photo-1544025162-d76694265547?w=800",
        "steak": "https://images.unsplash.com/photo-1600891964599-f61ba0e24092?w=800",
        "pork": "https://images.unsplash.com/photo-1627308595229-7830f5c9100f?w=800",
        "lamb": "https://images.unsplash.com/photo-1600891964599-f61ba0e24092?w=800",
        "meat": "https://images.unsplash.com/photo-1544025162-d76694265547?w=800",
        "ribs": "https://images.unsplash.com/photo-1544025162-d76694265547?w=800",
        "kebab": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800",
        
        # MAKARNA VE PİZZA
        "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800",
        "pasta": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800",
        "spaghetti": "https://images.unsplash.com/photo-1622973531268-8b22a014a04d?w=800",
        "macaroni": "https://images.unsplash.com/photo-1543339494-b4cd4f7ba686?w=800",
        "noodle": "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=800",
        "lasagna": "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=800",
        
        # DENİZ ÜRÜNLERİ
        "fish": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=800",
        "salmon": "https://images.unsplash.com/photo-1485921325833-c519f76c4927?w=800",
        "shrimp": "https://images.unsplash.com/photo-1565557612130-1b29d4d5e27a?w=800",
        "crab": "https://images.unsplash.com/photo-1565557612130-1b29d4d5e27a?w=800",
        "seafood": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=800",
        
        # FAST FOOD VE EKMEK
        "burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800",
        "sandwich": "https://images.unsplash.com/photo-1528735602780-2552fd46c7ab?w=800",
        "bread": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800",
        "toast": "https://images.unsplash.com/photo-1528735602780-2552fd46c7ab?w=800",
        "taco": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=800",
        "wrap": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=800",
        "fries": "https://images.unsplash.com/photo-1576107232684-1279f390859f?w=800",
        
        # ÇORBA VE SULU YEMEKLER
        "soup": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800",
        "stew": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800",
        "chili": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800",
        "curry": "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=800",
        "broth": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800",
        
        # SALATA VE SEBZELER
        "salad": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800",
        "vegetable": "https://images.unsplash.com/photo-1557844352-761f2565b4b6?w=800",
        "potato": "https://images.unsplash.com/photo-1518977676601-b53f82aba650?w=800",
        "tomato": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800",
        "carrot": "https://images.unsplash.com/photo-1557844352-761f2565b4b6?w=800",
        "mushroom": "https://images.unsplash.com/photo-1557844352-761f2565b4b6?w=800",
        "onion": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800",
        "spinach": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800",
        "bean": "https://images.unsplash.com/photo-1557844352-761f2565b4b6?w=800",
        "broccoli": "https://images.unsplash.com/photo-1557844352-761f2565b4b6?w=800",
        
        # KAHVALTI VE YUMURTA
        "egg": "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=800",
        "omelet": "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=800",
        "pancake": "https://images.unsplash.com/photo-1554520735-0a3b8b7d8b36?w=800",
        "waffle": "https://images.unsplash.com/photo-1554520735-0a3b8b7d8b36?w=800",
        "breakfast": "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=800",
        "bacon": "https://images.unsplash.com/photo-1600891964599-f61ba0e24092?w=800",
        
        # TATLILAR VE HAMUR İŞİ
        "cake": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800",
        "chocolate": "https://images.unsplash.com/photo-1505576399279-565b52d4bec7?w=800",
        "cookie": "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=800",
        "pie": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800",
        "dessert": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800",
        "ice cream": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800",
        "muffin": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800",
        "brownie": "https://images.unsplash.com/photo-1505576399279-565b52d4bec7?w=800",
        
        # PİRİNÇ VE TAHILLAR
        "rice": "https://images.unsplash.com/photo-1536304993881-06f9d77007b1?w=800",
        "risotto": "https://images.unsplash.com/photo-1536304993881-06f9d77007b1?w=800",
        "quinoa": "https://images.unsplash.com/photo-1536304993881-06f9d77007b1?w=800",
        "oat": "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=800",
        
        # SÜT ÜRÜNLERİ VE SOSLAR
        "cheese": "https://images.unsplash.com/photo-1486297678162-eb8a19b0a32d?w=800",
        "butter": "https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b?w=800",
        "cream": "https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b?w=800",
        "sauce": "https://images.unsplash.com/photo-1472476443507-c7a5948772bf?w=800",
        "dip": "https://images.unsplash.com/photo-1472476443507-c7a5948772bf?w=800",
        
        # MEYVELER VE İÇECEKLER
        "fruit": "https://images.unsplash.com/photo-1506368083636-6defb4b04dfa?w=800",
        "apple": "https://images.unsplash.com/photo-1506368083636-6defb4b04dfa?w=800",
        "banana": "https://images.unsplash.com/photo-1506368083636-6defb4b04dfa?w=800",
        "berry": "https://images.unsplash.com/photo-1506368083636-6defb4b04dfa?w=800",
        "smoothie": "https://images.unsplash.com/photo-1505252585461-04db1db14757?w=800",
        "drink": "https://images.unsplash.com/photo-1505252585461-04db1db14757?w=800",
        "juice": "https://images.unsplash.com/photo-1505252585461-04db1db14757?w=800",
        "coffee": "https://images.unsplash.com/photo-1497935586351-b67a49e012bf?w=800",
        "tea": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800"
    }
    
    # Eşleşme bulursa URL döndür
    for key, url in IMAGE_MAP.items():
        if key in text:
            return url
            
    # HİÇBİR EŞLEŞME OLMAZSA KENDİ LOGONU BAS (Sıfır risk)
    return "https://cdn-icons-png.flaticon.com/512/1830/1830839.png"
    

def get_recommendations(user_input, top_n=100):
    text = str(user_input).lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['RecipeIngredientParts'].apply(lambda x: re.sub(r'[^a-z\s]', ' ', str(x).lower())))
    
    user_vec = vectorizer.transform([text])
    sim_scores = cosine_similarity(user_vec, tfidf_matrix).flatten()
    top_indices = sim_scores.argsort()[-top_n:][::-1]
    
    results = []
    for idx in top_indices:
        if sim_scores[idx] > 0:
            results.append({
                'name': df.iloc[idx]['Name'],
                'ingredients': df.iloc[idx]['RecipeIngredientParts'],
                'minutes': df.iloc[idx]['TotalTime'],
                'calories': df.iloc[idx]['Calories'],
                'protein': df.iloc[idx]['ProteinContent'],
                'fat': df.iloc[idx]['FatContent'],
                'carbs': df.iloc[idx]['CarbohydrateContent'],
                'instructions': df.iloc[idx]['RecipeInstructions'],
                'local_image': get_image_for_recipe(df.iloc[idx]['Name']),
                'score': round(sim_scores[idx], 4)
            })
    return results