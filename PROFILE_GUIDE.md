# DietCheck Profile System - Complete Guide

## 🚀 Quick Start Guide

### How to Use Your Personal Dietary Profile

### Step 1: Set Your Profile (Once)
Tell G-Assist:
> *"Set my dietary profile: I'm allergic to milk and nuts, I'm vegan, have diabetes, avoid aspartame, and want max 5g sugar per 100g"*

**Or use the detailed profile:**
```json
{
  "profile_name": "User Special Needs Profile",
  "allergies": ["milk", "nuts", "soy"],
  "intolerances": ["gluten", "lactose"],
  "dietary_preferences": {
    "vegan": true,
    "vegetarian": false,
    "low_sugar": true,
    "low_salt": false,
    "low_saturated_fat": true
  },
  "medical_conditions": ["diabetes", "celiac_disease"],
  "avoid_additives": ["e951-aspartame"],
  "nutrient_limits": {
    "sugars_100g": 5,
    "salt_100g": 0.3,
    "saturated_fat_100g": 1.5
  }
}
```

### Step 2: Search Without Worrying About Restrictions
Now you can simply ask:
- *"Search for chocolate bars"*
- *"Find nutrition info for cookies"*
- *"What's in this barcode 123456789"*

**DietCheck automatically:**
- ✅ Loads your saved profile
- 🔍 Analyzes every product against your restrictions
- ⚠️ Shows warnings for problematic ingredients
- ✅ Highlights safe products
- 📊 Compares nutrients to your limits

### Step 3: Manage Your Profile
- **View current settings:** *"Show my dietary profile"*
- **Update restrictions:** *"Update my profile to include shellfish allergy"*
- **Clear all restrictions:** *"Clear my dietary profile"*

## 🎯 Key Benefits

### Before (Old Way):
- Had to mention allergies every time
- Repeated dietary preferences for each search
- No memory between sessions
- Manual checking of ingredients

### After (New Profile System):
- ✨ **Set once, use everywhere**
- 💾 **Automatically saved and loaded**
- 🔄 **Works across all sessions**
- 🤖 **Automatic safety analysis**
- ⚡ **Instant personalized results**

## 📁 File Locations
- **Profile Storage:** `%USERPROFILE%\DietCheck\dietcheck-profile.json`
- **Plugin Logs:** `%USERPROFILE%\DietCheck\dietcheck-plugin.log`

## 🔧 Profile Commands Summary

| Command | Purpose | Example |
|---------|---------|---------|
| `set_user_profile` | Create/update dietary profile | *"Set my dietary profile with milk allergy"* |
| `get_user_profile` | View current profile settings | *"Show my dietary profile"* |
| `clear_user_profile` | Remove all restrictions | *"Clear my dietary profile"* |
| `search_food_product` | Search with auto-analysis | *"Search for cereal"* |
| `get_product_nutrition` | Get nutrition with safety check | *"Nutrition for barcode 123456"* |

---

## 📋 Complete Profile Options Reference

### **Profile Identity**
- **`profile_name`** (string): A descriptive name for your profile
  - Example: `"John's Diabetes & Vegan Profile"`

### **🚨 Allergies** (array of strings)
Common allergens that must be completely avoided:
- `"milk"` / `"dairy"` - All dairy products
- `"eggs"` - Egg products
- `"fish"` - All fish varieties
- `"shellfish"` / `"crustaceans"` - Shrimp, crab, lobster, etc.
- `"tree_nuts"` / `"nuts"` - Almonds, walnuts, cashews, etc.
- `"peanuts"` - Peanut products
- `"wheat"` - Wheat-based products
- `"soy"` / `"soybeans"` - Soy products
- `"sesame"` - Sesame seeds and oil
- `"mustard"` - Mustard seeds and products
- `"celery"` - Celery and celeriac
- `"lupin"` - Lupin beans
- `"molluscs"` - Snails, mussels, oysters, etc.
- `"sulphites"` / `"sulfites"` - Sulfur dioxide preservatives

### **⚠️ Intolerances** (array of strings)
Substances that cause digestive issues or discomfort:
- `"lactose"` - Lactose intolerance
- `"gluten"` - Gluten sensitivity/intolerance
- `"fructose"` - Fructose malabsorption
- `"histamine"` - Histamine intolerance
- `"fodmap"` - FODMAP sensitivity
- `"caffeine"` - Caffeine sensitivity
- `"alcohol"` - Alcohol intolerance
- `"artificial_sweeteners"` - Aspartame, sucralose, etc.

### **🥗 Dietary Preferences** (object with boolean values)
Lifestyle and ethical food choices:
- `"vegan": true/false` - No animal products
- `"vegetarian": true/false` - No meat, but dairy/eggs OK
- `"pescatarian": true/false` - Fish OK, but no other meat
- `"halal": true/false` - Islamic dietary laws
- `"kosher": true/false` - Jewish dietary laws
- `"paleo": true/false` - Paleolithic diet
- `"keto": true/false` - Ketogenic diet
- `"low_carb": true/false` - Low carbohydrate diet
- `"low_sugar": true/false` - Minimal added sugars
- `"low_salt": true/false` - Low sodium intake
- `"low_fat": true/false` - Low total fat
- `"low_saturated_fat": true/false` - Low saturated fat
- `"high_protein": true/false` - High protein focus
- `"high_fiber": true/false` - High fiber focus
- `"organic_only": true/false` - Organic products preferred
- `"non_gmo": true/false` - Non-GMO products only
- `"raw_food": true/false` - Raw food diet
- `"whole_foods": true/false` - Minimally processed foods

### **🏥 Medical Conditions** (array of strings)
Health conditions requiring dietary management:
- `"diabetes"` / `"diabetes_type1"` / `"diabetes_type2"` - Blood sugar management
- `"celiac_disease"` - Strict gluten avoidance
- `"crohns_disease"` - Inflammatory bowel disease
- `"ulcerative_colitis"` - Inflammatory bowel condition
- `"ibs"` / `"irritable_bowel_syndrome"` - IBS management
- `"kidney_disease"` - Kidney function protection
- `"heart_disease"` / `"cardiovascular_disease"` - Heart health
- `"hypertension"` / `"high_blood_pressure"` - Blood pressure control
- `"high_cholesterol"` - Cholesterol management
- `"gout"` - Purine restriction
- `"osteoporosis"` - Bone health focus
- `"anemia"` - Iron deficiency management
- `"thyroid_disorder"` - Thyroid function support
- `"acid_reflux"` / `"gerd"` - Gastroesophageal reflux
- `"gallbladder_disease"` - Fat restriction
- `"liver_disease"` - Liver function support
- `"obesity"` - Weight management
- `"eating_disorder_recovery"` - Eating disorder support

### **🧪 Avoid Additives** (array of strings)
Specific additives and preservatives to avoid:
- **Artificial Sweeteners:**
  - `"e950-acesulfame-k"` - Acesulfame potassium
  - `"e951-aspartame"` - Aspartame
  - `"e952-cyclamate"` - Cyclamate
  - `"e954-saccharin"` - Saccharin
  - `"e955-sucralose"` - Sucralose
- **Preservatives:**
  - `"e200-sorbic-acid"` - Sorbic acid
  - `"e202-potassium-sorbate"` - Potassium sorbate
  - `"e210-benzoic-acid"` - Benzoic acid
  - `"e211-sodium-benzoate"` - Sodium benzoate
  - `"e220-sulfur-dioxide"` - Sulfur dioxide
  - `"e249-potassium-nitrite"` - Potassium nitrite
  - `"e250-sodium-nitrite"` - Sodium nitrite
- **Colorings:**
  - `"e102-tartrazine"` - Yellow coloring
  - `"e110-sunset-yellow"` - Orange coloring
  - `"e122-carmoisine"` - Red coloring
  - `"e124-ponceau-4r"` - Red coloring
  - `"e129-allura-red"` - Red coloring
- **Flavor Enhancers:**
  - `"e621-msg"` - Monosodium glutamate
  - `"e627-disodium-guanylate"` - Guanylate
  - `"e631-disodium-inosinate"` - Inosinate

### **📊 Nutrient Limits** (object with numeric values per 100g)
Customize maximum amounts for specific nutrients:
- **Macronutrients:**
  - `"energy_kcal_100g": 300` - Maximum calories per 100g
  - `"fat_100g": 10` - Maximum total fat (grams)
  - `"saturated_fat_100g": 3` - Maximum saturated fat (grams)
  - `"trans_fat_100g": 0.5` - Maximum trans fat (grams)
  - `"carbohydrates_100g": 50` - Maximum carbs (grams)
  - `"sugars_100g": 5` - Maximum sugars (grams)
  - `"fiber_100g": 3` - Minimum fiber (grams)
  - `"proteins_100g": 10` - Minimum protein (grams)
- **Minerals:**
  - `"salt_100g": 0.3` - Maximum salt (grams)
  - `"sodium_100g": 120` - Maximum sodium (milligrams)
  - `"potassium_100g": 200` - Minimum potassium (milligrams)
  - `"calcium_100g": 100` - Minimum calcium (milligrams)
  - `"iron_100g": 2` - Minimum iron (milligrams)
- **Vitamins:**
  - `"vitamin_c_100g": 10` - Minimum vitamin C (milligrams)
  - `"vitamin_d_100g": 5` - Minimum vitamin D (micrograms)

## 💡 Example Specialized Profiles

### **Diabetic Profile:**
```json
{
  "profile_name": "Diabetic Management",
  "dietary_preferences": {"low_sugar": true, "low_carb": true},
  "medical_conditions": ["diabetes_type2"],
  "nutrient_limits": {
    "sugars_100g": 3,
    "carbohydrates_100g": 20
  }
}
```

### **Severe Allergy Profile:**
```json
{
  "profile_name": "Multiple Allergies",
  "allergies": ["milk", "eggs", "nuts", "soy", "wheat"],
  "intolerances": ["gluten"],
  "dietary_preferences": {"organic_only": true}
}
```

### **Heart-Healthy Profile:**
```json
{
  "profile_name": "Heart Health",
  "medical_conditions": ["cardiovascular_disease", "high_cholesterol"],
  "dietary_preferences": {"low_saturated_fat": true, "low_salt": true},
  "nutrient_limits": {
    "saturated_fat_100g": 1.5,
    "salt_100g": 0.3,
    "trans_fat_100g": 0
  }
}
```

### **Family Profile with Kids:**
```json
{
  "profile_name": "Family Safe Foods",
  "allergies": ["peanuts"],
  "avoid_additives": ["e102-tartrazine", "e621-msg"],
  "dietary_preferences": {"organic_only": true, "whole_foods": true},
  "nutrient_limits": {
    "sugars_100g": 8,
    "salt_100g": 0.5
  }
}
```

---

## 🔧 Technical Notes

### **Profile Storage:**
- Location: `%USERPROFILE%\DietCheck\dietcheck-profile.json`
- Format: JSON with UTF-8 encoding
- Persistent across sessions and plugin restarts

### **Field Types:**
- **Strings**: `profile_name`
- **Arrays**: `allergies`, `intolerances`, `medical_conditions`, `avoid_additives`
- **Objects**: `dietary_preferences`, `nutrient_limits`
- **Booleans**: All fields within `dietary_preferences`
- **Numbers**: All fields within `nutrient_limits`

### **Validation:**
- All fields are optional
- Unknown fields are ignored
- Invalid values are skipped with warnings
- Empty profile is valid (no restrictions)
