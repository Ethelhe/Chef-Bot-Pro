import os
import streamlit as st
import pandas as pd
import re
import random
from ml_engine import get_recommendations

# ==========================================
# 1. SAYFA AYARLARI VE PROFESYONEL CSS
# ==========================================
st.set_page_config(page_title="Chef-Bot Pro", page_icon="👨‍🍳", layout="wide")

page_bg_img = """
<style>
.stApp {
    background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), url("https://images.unsplash.com/photo-1556910103-1c02745a872e?q=80&w=2000&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stSidebar"] {
    background-color: rgba(15, 15, 15, 0.95) !important;
    border-right: 1px solid #333;
}
div[data-testid="stVerticalBlock"] div[style*="border"] {
    background-color: rgba(25, 25, 25, 0.85) !important;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
h1, h2, h3, h4, h5, p, label, span { color: #F0F2F6 !important; }
.stButton>button {
    background-color: #FF4B4B; color: white; border-radius: 8px; border: none; transition: 0.3s;
}
.stButton>button:hover { background-color: #FF6B6B; }
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# ==========================================
# 2. STATE MANAGEMENT (HAFIZA YÖNETİMİ)
# ==========================================
# Kullanıcının uygulama içindeki gezinmelerini ve ayarlarını hafızada tutarız
if 'pantry' not in st.session_state: st.session_state.pantry = []
if 'diet' not in st.session_state: st.session_state.diet = "Normal"
if 'cuisine' not in st.session_state: st.session_state.cuisine = "All"
if 'max_cal' not in st.session_state: st.session_state.max_cal = 1500
if 'min_prot' not in st.session_state: st.session_state.min_prot = 0
if 'max_time' not in st.session_state: st.session_state.max_time = 60
if 'favorites' not in st.session_state: st.session_state.favorites = []

# ==========================================
# 3. YARDIMCI FONKSİYONLAR
# ==========================================
def parse_time(time_str):
    if pd.isna(time_str): return 999
    time_str = str(time_str)
    h = re.search(r'(\d+)H', time_str)
    m = re.search(r'(\d+)M', time_str)
    hours = int(h.group(1)) if h else 0
    mins = int(m.group(1)) if m else 0
    return hours * 60 + mins

def format_ingredients(ing_str):
    clean_str = str(ing_str).replace('c(', '').replace(')', '').replace('"', '').replace("'", "")
    return [i.strip().capitalize() for i in clean_str.split(',')]

# Favoriye ekleme işlemini sayfa yenilenmeden önce arka planda çözen fonksiyon (Callback)
def add_to_favorites(recipe, img_url):
    if not any(f['name'] == recipe['name'] for f in st.session_state.favorites):
        res_to_save = recipe.copy()
        res_to_save['image_url'] = img_url
        st.session_state.favorites.append(res_to_save)


# YENİ NESİL: GERÇEK ZAMANLI AI GÖRSEL ÜRETİCİ (Sonsuz Çeşitlilik!)
def get_dynamic_image(recipe_name, index):
    # Tarifin adını temizliyoruz
    clean_name = str(recipe_name).strip()
    
    # Yapay zekaya (AI) yemeğin nasıl görünmesi gerektiğini anlatan bir 'Prompt' yazıyoruz
    prompt = f"A delicious plate of {clean_name}, professional food photography, restaurant plating, high resolution, soft lighting"
    
    # URL'de boşluk ve özel karakter olamayacağı için bunları internet formatına çeviriyoruz
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Pollinations.ai servisi bu adrese gidildiği anda resmi saniyeler içinde 'çizip' bize gönderir
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true"

# ==========================================
# 4. SOL MENÜ (NAVİGASYON)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1830/1830839.png", width=60)
    st.markdown("## Chef-Bot Pro")
    st.caption("v2.0 - Final Build")
    st.divider()
    menu = st.radio("Navigation", [
        "🔍 Discover Recipes", 
        "🛒 Manage Pantry", 
        "❤️ My Saved Favorites",
        "⚖️ Set Meal Preferences", 
        "🎯 Nutritional Goals", 
        "⚙️ Settings"
    ])
    st.divider()
    st.success("Veritabanı: Aktif (Kaggle)\nModel: TF-IDF & Cosine")

# ==========================================
# 5. SAYFALAR VE MODÜLLER
# ==========================================

# --- YENİ EKLENEN FAVORİLER SAYFASI ---
if menu == "❤️ My Saved Favorites":
    st.title("❤️ My Saved Favorites")
    st.markdown("Kaydettiğiniz tüm harika tarifler burada!")
    
    if not st.session_state.favorites:
        st.warning("Henüz favorilere eklediğiniz bir tarif bulunmuyor. 'Discover Recipes' sekmesinden arama yapabilirsiniz.")
    else:
        cols = st.columns(3)
        for idx, fav in enumerate(st.session_state.favorites):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.image(fav['image_url'], use_container_width=True)
                    st.markdown(f"#### {str(fav['name']).title()}")
                    st.write(f"⏱️ **Süre:** {parse_time(fav['minutes'])} dk")
                    
                    if st.button("❌ Favorilerden Çıkar", key=f"del_{idx}_{fav['name']}"):
                        st.session_state.favorites.pop(idx)
                        st.rerun() # Sayfayı günceller

# --- SAYFA 2: MANAGE PANTRY (KİLER YÖNETİMİ) ---
if menu == "🛒 Manage Pantry":
    st.title("🛒 Manage Pantry")
    st.markdown("Evdeki malzemelerinizi buraya ekleyin. Yapay zeka arama yaparken öncelikle bu listeyi kullanacaktır.")
    
    with st.container(border=True):
        new_item = st.text_input("Yeni Malzeme Ekle (Örn: garlic)")
        if st.button("Ekle"):
            if new_item and new_item.lower() not in st.session_state.pantry:
                st.session_state.pantry.append(new_item.lower())
                st.success(f"{new_item} kilere eklendi!")
        
        st.markdown("### Mevcut Malzemeleriniz:")
        if st.session_state.pantry:
            # Malzemeleri şık etiketler (pills) gibi gösterelim
            cols = st.columns(4)
            for i, item in enumerate(st.session_state.pantry):
                cols[i % 4].info(item.capitalize())
            
            if st.button("Kileri Temizle"):
                st.session_state.pantry = []
                st.rerun()
        else:
            st.warning("Kileriniz şu an boş.")

# --- SAYFA 3: MEAL PREFERENCES (DİYET VE MUTFAK) ---
elif menu == "⚖️ Set Meal Preferences":
    st.title("⚖️ Set Meal Preferences")
    st.markdown("Uygulama genelindeki tüm aramalarınız için varsayılan diyet ve mutfak tercihlerinizi belirleyin.")
    
    with st.container(border=True):
        st.session_state.diet = st.selectbox("Dietary Preferences", ["Normal", "Vegetarian", "Vegan", "Low-Carb"], index=["Normal", "Vegetarian", "Vegan", "Low-Carb"].index(st.session_state.diet))
        st.session_state.cuisine = st.selectbox("Cuisine Preferences", ["All", "Italian (Pasta/Pizza)", "American (Burger/Steak)"], index=["All", "Italian (Pasta/Pizza)", "American (Burger/Steak)"].index(st.session_state.cuisine))
        st.success("Tercihleriniz otomatik olarak kaydedildi.")

# --- SAYFA 4: NUTRITIONAL GOALS (BESİN HEDEFLERİ) ---
elif menu == "🎯 Nutritional Goals":
    st.title("🎯 Nutritional Goals")
    st.markdown("Günlük makro hedeflerinize uygun tarifleri filtrelemek için sınırlarınızı belirleyin.")
    
    with st.container(border=True):
        st.session_state.max_cal = st.slider("Maximum Kalori (Öğün başı):", 100, 3000, st.session_state.max_cal, 50)
        st.session_state.min_prot = st.slider("Minimum Protein (g):", 0, 100, st.session_state.min_prot, 5)
        st.session_state.max_time = st.slider("Maximum Hazırlama Süresi (dk):", 10, 180, st.session_state.max_time, 5)
        st.success("Besin hedefleriniz güncellendi.")

# --- SAYFA 5: SETTINGS (AYARLAR) ---
elif menu == "⚙️ Settings":
    st.title("⚙️ Settings")
    with st.container(border=True):
        st.write("**Hesap Bilgileri:** Muhammed Mansur Güney")
        st.write("**Model Konfigürasyonu:** Content-Based Filtering (Cosine Similarity)")
        st.write("**UI Framework:** Streamlit")
        st.toggle("Dark Mode", value=True, disabled=True)
        st.toggle("Push Notifications", value=False)
        if st.button("Logout"):
            st.warning("MVP sürümünde çıkış yapılamaz.")

# --- SAYFA 1: DISCOVER RECIPES (ANA ARAMA MOTORU) ---
elif menu == "🔍 Discover Recipes":
    st.title("🔍 Discover Recipes")
    
    # Kullanıcıya Kiler bilgisini verelim
    pantry_str = ", ".join(st.session_state.pantry) if st.session_state.pantry else ""
    
    with st.container(border=True):
        st.markdown("##### 📝 Ne Pişirmek İstiyorsunuz?")
        user_input = st.text_input("Arama yapın (Boş bırakırsanız 'Manage Pantry' deki kiler malzemeleriniz kullanılır):", value=pantry_str)
        
        # O anki aktif filtreleri küçük etiketlerle gösterelim ki profesyonel dursun
        st.markdown(f"*Aktif Filtreler: **{st.session_state.diet}** Diyet | **{st.session_state.cuisine}** Mutfak | Maks **{st.session_state.max_cal}** kcal | Min **{st.session_state.min_prot}**g Protein | Maks **{st.session_state.max_time}** dk*")

    if st.button("🍽️ Tarif Bul (AI Mode)", use_container_width=True):
        search_query = user_input if user_input else pantry_str
        
        if not search_query:
            st.error("Lütfen arama çubuğuna malzeme girin veya 'Manage Pantry' sekmesinden kilerinize malzeme ekleyin.")
        else:
            st.markdown("### 🌟 Size Özel Öneriler")
            with st.spinner('Yapay Zeka Mutfakta Çalışıyor, Filtreler Uygulanıyor...'):
                # Çok fazla filtre kullanacağımız için ML'den bolca sonuç alıyoruz (Top 100)
                raw_results = get_recommendations(search_query, top_n=100)
                
                filtered_results = []
                for r in raw_results:
                    # 1. NUTRITIONAL & TIME FILTERS
                    if parse_time(r['minutes']) > st.session_state.max_time: continue
                    cal = float(r['calories']) if pd.notna(r['calories']) else 0
                    prot = float(r['protein']) if pd.notna(r['protein']) else 0
                    if cal > st.session_state.max_cal: continue
                    if prot < st.session_state.min_prot: continue
                        
                    # 2. DIETARY FILTERS
                    ing_text = str(r['ingredients']).lower()
                    if st.session_state.diet == "Vegetarian" and any(meat in ing_text for meat in ['chicken', 'beef', 'pork', 'turkey', 'fish', 'meat']): continue
                    if st.session_state.diet == "Vegan" and any(animal in ing_text for animal in ['chicken', 'beef', 'pork', 'fish', 'cheese', 'milk', 'butter', 'egg', 'honey', 'yogurt']): continue
                    if st.session_state.diet == "Low-Carb" and float(r['carbs'] if pd.notna(r['carbs']) else 0) > 30: continue
                        
                    # 3. CUISINE FILTERS
                    name_text = str(r['name']).lower()
                    if st.session_state.cuisine == "Italian (Pasta/Pizza)" and not any(it in name_text for it in ['pasta', 'pizza', 'spaghetti', 'lasagna', 'ravioli', 'macaroni']): continue
                    if st.session_state.cuisine == "American (Burger/Steak)" and not any(am in name_text for am in ['burger', 'steak', 'bbq', 'fries', 'mac', 'cheese']): continue
                        
                    filtered_results.append(r)

                # HER SEFERİNDE BİRAZ FARKLI SONUÇLAR GELSİN DİYE İLK 10 İÇİNDEN RASTGELE 3 SEÇ
                if len(filtered_results) >= 3:
                    top_pool = filtered_results[:10]
                    results = random.sample(top_pool, 3)
                    # Skorlara göre tekrar büyükten küçüğe sırala
                    results = sorted(results, key=lambda x: x['score'], reverse=True)
                else:
                    results = filtered_results[:3]

            if results:
                cols = st.columns(3)
                for idx, col in enumerate(cols):
                    res = results[idx]
                    with col:
                        with st.container(border=True):

                            ai_img_url = res['local_image']
                            
                            st.markdown(
                                f'<img src="{ai_img_url}" style="width:100%; border-radius:12px; margin-bottom:10px;">', 
                                unsafe_allow_html=True
                            )
                            
                            st.markdown(f"#### {str(res['name']).title()}")
                            st.success(f"**AI Match Score:** %{int(res['score']*100)}")

                            c1, c2, c3 = st.columns(3)
                            c1.metric("Kcal", f"{res['calories']}")
                            c2.metric("Prot", f"{res['protein']}g")
                            c3.metric("Karb", f"{res['carbs']}g")

                            with st.expander("📖 Hazırlanışı & Malzemeler"):
                                st.write(f"⏱️ **Süre:** {parse_time(res['minutes'])} dk")
                                st.markdown("**Malzemeler:**")
                                clean_ings = format_ingredients(res['ingredients'])
                                for ing in clean_ings:
                                    st.markdown(f"- {ing}")
                                st.divider()
                                # TARİF ADIMLARI 
                                st.markdown("**Hazırlanışı:**")
                                raw_instructions = str(res.get('instructions', 'Tarif detayı bulunamadı.'))
                                # Veri setindeki gereksiz parantezleri temizle
                                clean_instructions = raw_instructions.replace('c(', '').replace(')', '').replace('"', '').replace("'", "")
                                
                                # Adımları virgülle ayırıp alt alta yazdır
                                steps = [step.strip() for step in clean_instructions.split(',') if step.strip()]
                                for idx_step, step in enumerate(steps):
                                    st.write(f"**{idx_step + 1}.** {step.capitalize()}")

                            unique_id = abs(hash(str(res['ingredients'])))
                            st.button(
                                "❤️ Favorilere Ekle",
                                key=f"fav_{idx}_{hash(res['name'])}",
                                on_click=add_to_favorites,
                                args=(res, res['local_image'])
                            )
            else:
                st.error("Bu zorlu kriterlere uygun tarif bulamadık! Lütfen yan menülerden (Diet, Nutrients) filtrelerinizi biraz esnetin.")