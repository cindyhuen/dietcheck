

🚀 G-Assist Hackathon Project

This project is a submission for the G-Assist Plug-in Hackathon, organized by NVIDIA. 


# DietCheck Plugin for NVIDIA G-Assist

DietCheck is a G-Assist plugin that helps users instantly determine whether a food item fits their personal dietary needs. It provides clear safety indicators, nutritional details, and ingredient information using data from the Open Food Facts database — making diet tracking faster and smarter.

## What Can It Do?
- 🔍 Search for food products by name
- 🎯 **NEW: Search ONLY safe foods** - Filter results to show only foods you can safely eat
- 📊 Get detailed nutritional information including:
  - Calories per 100g
  - Fat content
  - Sugar content
  - Protein content (with min/max filtering options)
  - Salt content
  - Fiber content
- 📱 Look up products by barcode for precise information
- 🌍 Access data from the world's largest open food database
- 🔐 **Enhanced Personal Dietary Profile System**
  - **Set once, use everywhere**: Configure your profile once and it's automatically applied to all searches
  - **Persistent storage**: Your profile is saved and loaded automatically every time
  - **Comprehensive settings**: Allergies, intolerances, medical conditions, dietary preferences
  - **Custom nutrient limits**: Set personalized limits for sugar, salt, fat, etc.
  - **Automatic safety analysis**: Every product is instantly analyzed against your profile
  - **Profile management**: Easy commands to view, update, or clear your profile
- ⚠️ **Smart Safety Warnings** - Products are automatically analyzed against your profile
- ✅ **Safety Indicators** - Clear visual indicators (✅ SAFE, ⚠️ CAUTION, ❌ NOT SAFE)
- 🎯 **Safe Food Filter** - Show only foods that meet ALL your dietary requirements
- 📝 **Detailed logging** for troubleshooting

## 🛠️ Before You Start
Make sure you have:
- ✅ Windows PC
- ✅ Python 3.6 or higher installed
- ✅ NVIDIA G-Assist installed
- ✅ Internet connection (for API access)

## 🚀 Quickstart

### 📥 Step 1: Get the Files
```bash
git clone https://github.com/cindyhuen/dietcheck.git
```


### ⚙️ Step 2: Setup and Build

**💡 Note**: Commands differ slightly between Command Prompt and PowerShell.

1. **Run the setup script:**

   **In Command Prompt (CMD):**
   ```cmd
   setup.bat
   ```
   
   **In PowerShell:**
   ```powershell
   .\setup.bat
   ```
   
   This installs all required Python packages including `requests` for API calls.

2. **Run the build script:**

   **In Command Prompt (CMD):**
   ```cmd
   build.bat
   ```
   
   **In PowerShell:**
   ```powershell
   .\build.bat
   ```
   
   This creates the executable and prepares all necessary files.

### 📦 Step 3: Install the Plugin
1. Navigate to the `dist` folder created by the build script
2. Copy the `dietcheck` folder to:
```bash
%PROGRAMDATA%\NVIDIA Corporation\nvtopps\rise\plugins
```

💡 **Tip**: Make sure all files are copied, including:
- The executable (`dietcheck-plugin.exe`)
- `manifest.json`
- All dependency files

## 🧪 Testing the Plugin

### 📋 Test Script Available
A comprehensive test script is included to help you verify the plugin is working correctly:

**📁 File**: `test-script.md` - Contains PowerShell commands and JSON test cases for all functions

**🚀 Quick Test Commands** (run from DietCheck directory):
```powershell
# Test basic search
echo '{"tool_calls":[{"func":"search_food_product","params":{"product_name":"bread"}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

# Test protein filtering - high protein products
echo '{"tool_calls":[{"func":"search_food_product","params":{"product_name":"yogurt","min_protein":10}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

# Test protein filtering - low protein products  
echo '{"tool_calls":[{"func":"search_food_product","params":{"product_name":"bread","max_protein":5}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

# Test calorie filtering - high calorie products
echo '{"tool_calls":[{"func":"search_food_product","params":{"product_name":"energy bar","min_calories":300}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

# Test fiber filtering - high fiber products
echo '{"tool_calls":[{"func":"search_food_product","params":{"product_name":"cereal","min_fiber":8}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

# Test safe food search (requires profile)
echo '{"tool_calls":[{"func":"search_safe_food_only","params":{"product_name":"bread"}}]}' | .\dist\dietcheck\dietcheck-plugin.exe
```

**📚 What's Included:**
- ✅ All 7 main functions with examples
- ✅ Error handling test cases  
- ✅ Step-by-step testing guide
- ✅ Expected results for each test
- ✅ Recommended testing order

**💡 Testing Tips:**
1. Start by setting your dietary profile
2. Compare regular search vs safe-only search results
3. Test nutrition lookup with specific barcodes
4. See `test-script.md` for complete details

## 🍎 Usage Examples

### Search for Safe Foods Only
Ask G-Assist: *"Find safe bread options for my diet"* or *"Show only safe snacks"*
- This will use the new `search_safe_food_only` function
- Returns ONLY products that are completely safe for your dietary profile
- Filters out any products with allergens, prohibited ingredients, or nutrient limit violations
- Perfect for quick shopping when you only want to see foods you can safely eat

### Search for All Food Products (with warnings)
Ask G-Assist: *"Search for coca cola nutrition"*
- This will use the `search_food_product` function
- Returns a list of matching products with their barcodes
- Shows safety indicators: ✅ SAFE, ⚠️ CAUTION, ❌ NOT SAFE
- Includes detailed warnings about potential dietary conflicts

### Get Detailed Nutrition Information
Ask G-Assist: *"Get nutrition info for barcode 737628064502"*
- This will use the `get_product_nutrition` function
- Returns detailed nutritional breakdown
- Shows calories, macros, and other nutritional data

### Example Queries You Can Try:

**Basic Nutrition Queries:**
- *"Find nutrition info for banana"*
- *"Search for cheese pizza"*
- *"What's the calorie content of barcode 1234567890123"*
- *"Show me nutritional information for chocolate"*

**Protein-Focused Queries:**
- *"Find high-protein yogurt with at least 15g protein"* (uses `min_protein`)
- *"Search for low-protein bread with maximum 5g protein"* (uses `max_protein`)
- *"Show me protein bars between 20-30g protein"* (uses both `min_protein` and `max_protein`)
- *"Find cereals with minimum 10g protein per 100g"*

**Calorie and Fiber-Focused Queries:**
- *"Find high-calorie energy bars with at least 400 calories"* (uses `min_calories`)
- *"Search for high-fiber bread with minimum 8g fiber"* (uses `min_fiber`)
- *"Show me low-calorie snacks with maximum 100 calories"* (uses `max_calories`)
- *"Find foods with both high fiber (min 5g) and high calories (min 300)"* (uses both `min_fiber` and `min_calories`)

**Profile-Aware Queries:**
- *"Set my dietary profile with milk allergy and vegan preference"*
- *"What's my current dietary profile?"*
- *"Search for breakfast cereals"* (will show safety warnings based on your profile)
- *"Is this product safe for my diet?"* (when checking specific nutrition info)

## 📊 API Information

The plugin uses the **Open Food Facts API**:

### Search Endpoint:
- **URL**: `https://world.openfoodfacts.org/cgi/search.pl?search_terms={product_name}&search_simple=1&action=process&json=1`
- **Example**: `https://world.openfoodfacts.org/cgi/search.pl?search_terms=coca+cola&search_simple=1&action=process&json=1`

### Product Details Endpoint:
- **URL**: `https://world.openfoodfacts.org/api/v0/product/{barcode}.json`
- **Example**: `https://world.openfoodfacts.org/api/v0/product/737628064502.json`

## 🔧 Technical Details

### Functions Available:
1. **`search_food_product`**
   - Parameters: 
     - `product_name` (string, required)
     - Optional filters: `low_fat`, `low_fiber`, `low_sugar`, `low_salt`, `no_nuts`
     - Custom limits: `min_calories`, `max_calories`,  `max_fat`, `min_fiber`, `max_fiber`, `max_sugar`, `max_salt`, `min_protein`, `max_protein`
   - Returns: List of matching food products with barcodes and safety indicators (✅ SAFE, ⚠️ CAUTION, ❌ NOT SAFE)
   
2. **`search_safe_food_only`** 🎯 NEW
   - Parameter: `product_name` (string, required)
   - Returns: ONLY products that are completely safe for your dietary profile
   - Filters out all products with warnings or dietary conflicts
   - Perfect for finding foods you can safely eat without worrying
   
3. **`get_product_nutrition`**
   - Parameter: `barcode` (string, required)
   - Returns: Detailed nutritional information with safety analysis

4. **`set_user_profile`** ⭐ 
   - Parameters: Profile object with allergies, preferences, limits
   - Returns: Confirmation of profile setup
   
5. **`get_user_profile`** ⭐ 
   - Parameters: None
   - Returns: Current user profile settings and restrictions
   
6. **`clear_user_profile`** ⭐ 
   - Parameters: None
   - Returns: Confirmation that profile has been cleared

7. **`analyze_product_safety`** 🔒 INTERNAL
   - Used internally to analyze products against user profiles
   - Supports both regular and strict mode filtering

### Response Format:
```json
{
  "success": true,
  "message": "Coca-Cola Classic (Coca-Cola): Energy: 139 kcal/100g, Fat: 0g, Sugar: 10.6g, Protein: 0g, Salt: 0.01g"
}
```

## 🐛 Troubleshooting

### Common Issues:
1. **"No products found"**: Try different search terms or check spelling
2. **"Product not found"**: Verify the barcode is correct and exists in the database
3. **"Request timed out"**: Check your internet connection
4. **Plugin not responding**: Check the log file at `%USERPROFILE%\DietCheck\dietcheck-plugin.log`

### Log Location:
The plugin creates detailed logs at: `%USERPROFILE%\DietCheck\dietcheck-plugin.log`

## 🔐 Personal Dietary Profile System

### ⚙️ Setting Up Your Profile (One-Time Setup)

Set your dietary profile once, and DietCheck will automatically apply it to all future searches:

**Example Profile Setup:**
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

**📚 For a comprehensive list of all available profile options, see: [`PROFILE_GUIDE.md`](PROFILE_GUIDE.md)**

**Tell G-Assist:** *"Set my dietary profile with allergies to milk and nuts, vegan preferences, and diabetes considerations"*

### 📋 Profile Commands

- **View Profile:** *"Show my current dietary profile"*
- **Update Profile:** *"Update my dietary profile with new restrictions"*
- **Clear Profile:** *"Clear my dietary profile"*

### ✨ Automatic Benefits

Once your profile is set:
- **🔄 Persistent Storage**: Saved to `%USERPROFILE%\DietCheck\dietcheck-profile.json`
- **🚀 Auto-Load**: Automatically loaded every time the plugin starts
- **🔍 Smart Analysis**: Every food search automatically checks against your restrictions
- **⚠️ Instant Warnings**: Immediate safety alerts for problematic products
- **✅ Peace of Mind**: Clear indicators for safe products

**No more typing restrictions every time!** Just search for food and get personalized results instantly.

---

**Happy tracking! 🥗📊**

Copyright 2025 Cindy Huen. Licensed under the Apache License, version 2.0.