# DietCheck Plugin Test Script

**Note:** This script is intended to be run in **PowerShell**.

---

# 1. Search for Food Products - Returns list of matching products with safety indicators
echo '{"tool_calls":[{"func":"search_food_product","params":{"product_name":"coca cola"}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

## 1b. Alternative search examples - pizza
echo '{"tool_calls":[{"func":"search_food_product","params":{"product_name":"pizza"}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

## 1c. Alternative search examples - pizza with low fiber and low fat
echo '{"tool_calls":[{"func":"search_food_product","params":{"product_name":"pizza", "low_fiber":true, "low_fat":true}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

## 1d. Alternative search examples - energy bar with low sugar and max fiber 6g
echo '{"tool_calls":[{"func":"search_food_product","params":{"product_name":"energy bar", "low_sugar":true, "max_fiber":6.0}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

## 1d. Alternative search examples - yogurt with high protein (min 10g) and low sugar (max 4g)
echo '{"tool_calls":[{"func":"search_food_product","params":{"product_name":"yogurt", "min_protein":10.0, "max_sugar":4.0}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

# 2. Search Safe Food Only - Returns ONLY products safe for your dietary profile (requires profile setup)
echo '{"tool_calls":[{"func":"search_safe_food_only","params":{"product_name":"bread"}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

# 3. Get Product Nutrition - Get detailed nutritional information by barcode
echo '{"tool_calls":[{"func":"get_product_nutrition","params":{"barcode":"737628064502"}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

# 4. Set User Profile - Configure your dietary restrictions and preferences (one-time setup)
echo '{"tool_calls":[{"func":"set_user_profile","params":{"profile_name":"User Special Needs Profile","allergies":["milk","nuts","soy"],"intolerances":["gluten","lactose"],"dietary_preferences":{"vegan":true,"vegetarian":false,"low_sugar":true,"low_salt":false,"low_saturated_fat":true},"medical_conditions":["diabetes","celiac_disease"],"avoid_additives":["e951-aspartame"],"nutrient_limits":{"sugars_100g":5,"salt_100g":0.3,"saturated_fat_100g":1.5}}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

## 4b. Alternative Set User Profile - Simple vetarian-only profile
echo '{"tool_calls":[{"func":"set_user_profile","params":{"profile_name":"Simple Vegetarian Profile","allergies":[],"intolerances":[],"dietary_preferences":{"vegetarian":true},"medical_conditions":[],"avoid_additives":[],"nutrient_limits":{}}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

## 4c. Alternative Set User Profile - vegan + nuts allergy
echo '{"tool_calls":[{"func":"set_user_profile","params":{"profile_name":"Vegan + Nuts Allergy Profile","allergies":["nuts"],"intolerances":[],"dietary_preferences":{"vegan":true},"medical_conditions":[],"avoid_additives":[],"nutrient_limits":{}}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

## 4d. Alternative Set User Profile - vegetarian profile
echo '{"tool_calls":[{"func":"set_user_profile","params":{"profile_name":"Vegetarian Profile","allergies":[],"intolerances":[],"dietary_preferences":{"vegetarian":true},"medical_conditions":[],"avoid_additives":[],"nutrient_limits":{}}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

## 4e. Alternative Set User Profile - vegetarian + milk allergy
echo '{"tool_calls":[{"func":"set_user_profile","params":{"profile_name":"Vegetarian + Milk Allergy Profile","allergies":["milk"],"intolerances":[],"dietary_preferences":{"vegetarian":true},"medical_conditions":[],"avoid_additives":[],"nutrient_limits":{}}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

## 4f. Alternative Set User Profile -nuts allergy
echo '{"tool_calls":[{"func":"set_user_profile","params":{"profile_name":"Nuts Allergy Profile","allergies":["nuts"],"intolerances":[],"dietary_preferences":{},"medical_conditions":[],"avoid_additives":[],"nutrient_limits":{}}}]}' | .\dist\dietcheck\dietcheck-plugin.exe 

# 5. Get User Profile - View your current dietary profile settings
echo '{"tool_calls":[{"func":"get_user_profile","params":{}}]}' | .\dist\dietcheck\dietcheck-plugin.exe

# 6. Clear User Profile - Remove your dietary profile and start fresh
echo '{"tool_calls":[{"func":"clear_user_profile","params":{}}]}' | .\dist\dietcheck\dietcheck-plugin.exe
