"""
DietCheck Plugin - Nutritional information provider using Open Food Facts API.
Supports food search, barcode lookup, dietary profile management, and specialized filtering.
"""

import json
import sys
import requests
import logging
import os
import re
import ast
from ctypes import byref, windll, wintypes
from typing import Optional, Dict, Any

# Type definitions
Response = Dict[str, Any]

# Global user profile for dietary restrictions and preferences
USER_PROFILE = None
PROFILE_DIR = os.path.join(os.environ.get('USERPROFILE', '.'), 'DietCheck')
PROFILE_FILE = os.path.join(PROFILE_DIR, 'dietcheck-profile.json')

# Configure logging with a detailed format
LOG_FILE = os.path.join(PROFILE_DIR, 'dietcheck-plugin.log')

# Create the directory for logs if it doesn't exist
os.makedirs(PROFILE_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)

def safe_parse_parameter(param_value, expected_type):
    """
    Safely parse a parameter that might be a string representation of a Python object.
    
    Args:
        param_value: The parameter value to parse
        expected_type: The expected type (list, dict, str, etc.)
    
    Returns:
        The parsed parameter value or the original if already correct type
    """
    if param_value is None:
        return None
    
    # If already the correct type, return as-is
    if isinstance(param_value, expected_type):
        return param_value
    
    # If it's a string, try to parse it
    if isinstance(param_value, str):
        # Handle empty strings
        if not param_value.strip():
            return expected_type() if expected_type in [list, dict] else param_value
        
        try:
            # Try JSON parsing first (handles "true"/"false" properly)
            parsed = json.loads(param_value)
            if isinstance(parsed, expected_type):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        
        try:
            # Try ast.literal_eval for Python literals
            parsed = ast.literal_eval(param_value)
            if isinstance(parsed, expected_type):
                return parsed
        except (ValueError, SyntaxError):
            pass
        
        # If expected type is list/dict and we have a string, try to create empty one
        if expected_type in [list, dict]:
            logging.warning(f"Could not parse parameter '{param_value}' as {expected_type.__name__}, using empty {expected_type.__name__}")
            return expected_type()
    
    # Return original value if parsing failed
    logging.warning(f"Parameter '{param_value}' is not of expected type {expected_type.__name__}")
    return param_value

def save_user_profile():
    """Save the current user profile to a persistent file."""
    global USER_PROFILE, PROFILE_FILE, PROFILE_DIR
    
    if USER_PROFILE is not None:
        try:
            # Create DietCheck directory if it doesn't exist
            os.makedirs(PROFILE_DIR, exist_ok=True)
            
            with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
                json.dump(USER_PROFILE, f, indent=2, ensure_ascii=False)
            logging.info(f"User profile saved to {PROFILE_FILE}")
        except Exception as e:
            logging.error(f"Failed to save user profile: {str(e)}")

def load_user_profile():
    """Load the user profile from the persistent file."""
    global USER_PROFILE, PROFILE_FILE
    
    try:
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
                USER_PROFILE = json.load(f)
            profile_name = USER_PROFILE.get("profile_name", "Saved Profile")
            logging.info(f"User profile loaded: {profile_name}")
            return True
        else:
            logging.info("No saved user profile found")
            return False
    except Exception as e:
        logging.error(f"Failed to load user profile: {str(e)}")
        USER_PROFILE = None
        return False

def search_food_product(params: dict = None) -> dict:
    """Search for food products with optional nutrient filtering.
    
    Args:
        params (dict): Dictionary containing search parameters:
            - product_name (str, required): Name of the product to search for
            - low_fat (bool): Filter for low fat products (≤3.0g)
            - low_fiber (bool): Filter for low fiber products (≤3.0g) 
            - low_sugar (bool): Filter for low sugar products (≤5.0g)
            - low_salt (bool): Filter for low salt products (≤0.3g)
            - no_nuts (bool): Filter out products containing nuts
            - max_calories (float): Maximum calories per 100g
            - min_calories (float): Minimum calories per 100g
            - max_fat (float): Maximum fat content per 100g
            - max_fiber (float): Maximum fiber content per 100g
            - min_fiber (float): Minimum fiber content per 100g
            - max_sugar (float): Maximum sugar content per 100g
            - max_salt (float): Maximum salt content per 100g
            - min_protein (float): Minimum protein content per 100g
            - max_protein (float): Maximum protein content per 100g
    
    Returns:
        dict: Search results with product information and safety indicators
    """
    if not params or "product_name" not in params:
        logging.error("Product name parameter is required in search_food_product")
        return {"success": False, "message": "Product name parameter is required."}
    
    product_name = params["product_name"]
    
    # Extract filtering parameters
    filters = {
        'low_fat': params.get('low_fat', False),
        'low_fiber': params.get('low_fiber', False),
        'low_sugar': params.get('low_sugar', False),
        'low_salt': params.get('low_salt', False),
        'no_nuts': params.get('no_nuts', False),
        'max_calories': params.get('max_calories'),
        'min_calories': params.get('min_calories'),
        'max_fat': params.get('max_fat'),
        'max_fiber': params.get('max_fiber'),
        'min_fiber': params.get('min_fiber'),
        'max_sugar': params.get('max_sugar'),
        'max_salt': params.get('max_salt'),
        'min_protein': params.get('min_protein'),
        'max_protein': params.get('max_protein')
    }
    
    # Set default limits for "low" filters
    fat_limit = filters['max_fat'] if filters['max_fat'] is not None else (3.0 if filters['low_fat'] else None)
    fiber_limit = filters['max_fiber'] if filters['max_fiber'] is not None else (3.0 if filters['low_fiber'] else None)
    sugar_limit = filters['max_sugar'] if filters['max_sugar'] is not None else (5.0 if filters['low_sugar'] else None)
    salt_limit = filters['max_salt'] if filters['max_salt'] is not None else (0.3 if filters['low_salt'] else None)
    calorie_limit = filters['max_calories']
    min_calorie_limit = filters['min_calories']
    min_fiber_limit = filters['min_fiber']
    min_protein_limit = filters['min_protein']
    max_protein_limit = filters['max_protein']
    # Format the product name for URL (replace spaces with +)
    formatted_name = product_name.replace(" ", "+")
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={formatted_name}&search_simple=1&action=process&json=1"
    
    try:
        response = requests.get(url, timeout=80)
        if response.status_code == 200:
            search_data = response.json()
            
            products = search_data.get('products', [])
            if not products:
                logging.info(f"No products found for: {product_name}")
                return {
                    "success": True,
                    "message": f"No products found for '{product_name}'. Try a different search term."
                }
            
            # Format the first few results with safety analysis
            results = []
            profile_warnings = []
            filtered_results = []
            total_checked = 0
            
            # Helper function to check nutrient filters
            def meets_nutrient_filters(product):
                """Check if product meets the specified nutrient filtering criteria"""
                nutriments = product.get('nutriments', {})
                ingredients_text = product.get('ingredients_text', '').lower()
                allergens = product.get('allergens_tags', [])
                
                # Check nuts filter
                if filters['no_nuts']:
                    nuts_keywords = [
                        'nuts', 'nut', 'almond', 'walnut', 'peanut', 'cashew', 
                        'pistachio', 'hazelnut', 'pecan', 'macadamia', 'brazil nut',
                        'pine nut', 'chestnut', 'beechnut', 'hickory nut',
                        'may contain nuts', 'may contain nut', 'tree nuts'
                    ]
                    
                    # Check allergens tags for nut-related allergens
                    has_nut_allergen = any('nut' in allergen.lower() for allergen in allergens)
                    
                    # Check ingredients text for nut keywords
                    has_nut_ingredient = any(nut in ingredients_text for nut in nuts_keywords)
                    
                    # Check additional fields where nuts might be mentioned, but be smart about percentages
                    additional_fields_to_check = [
                        product.get('product_name', '').lower(),
                        product.get('generic_name', '').lower(),
                        product.get('categories', '').lower(),
                        product.get('labels', '').lower(),
                        product.get('traces', '').lower(),
                        product.get('ingredients_analysis_tags', []),
                        product.get('categories_tags', []),
                        product.get('labels_tags', [])
                    ]
                    
                    # Check nutriments field more carefully for percentage values
                    nutriments_str = str(product.get('nutriments', {})).lower()
                    has_nut_in_nutriments = False
                    if any(nut in nutriments_str for nut in nuts_keywords):
                        # Found nuts keywords in nutriments, now check if percentage is > 0
                        import re
                        # Look for patterns like "nuts...X%" where X is the percentage
                        # Match the entire phrase containing nuts and extract the percentage
                        nuts_percentage_matches = re.findall(r'[^{}\'"]*(?:nuts|nut|walnut|almond|peanut|cashew|pistachio|hazelnut|pecan|macadamia)[^{}\'"]*?(\d+(?:\.\d+)?)\s*%', nutriments_str, re.IGNORECASE)
                        
                        if nuts_percentage_matches:
                            # Check if any percentage is > 0
                            for percentage_str in nuts_percentage_matches:
                                try:
                                    percentage = float(percentage_str)
                                    if percentage > 0:
                                        has_nut_in_nutriments = True
                                        break
                                except ValueError:
                                    continue
                        else:
                            # If no percentage pattern found but nuts keyword exists, check if it's a general mention
                            # But be conservative - don't flag unless we're sure
                            if any(phrase in nutriments_str for phrase in ['may contain nuts', 'may contain nut', 'contains nuts', 'contains nut']):
                                has_nut_in_nutriments = True
                    
                    # Check all other additional fields for nuts keywords (excluding nutriments which we handled above)
                    has_nut_in_additional_fields = False
                    for field in additional_fields_to_check:
                        if isinstance(field, str):
                            if any(nut in field for nut in nuts_keywords):
                                has_nut_in_additional_fields = True
                                break
                        elif isinstance(field, list):
                            if any(any(nut in str(item).lower() for nut in nuts_keywords) for item in field):
                                has_nut_in_additional_fields = True
                                break
                    
                    if has_nut_allergen or has_nut_ingredient or has_nut_in_nutriments or has_nut_in_additional_fields:
                        return False, "Contains nuts"
                
                # Check nutrient limits
                limits = [
                    (calorie_limit, 'energy-kcal_100g', 'energy-kcal', 'Calories'),
                    (fat_limit, 'fat_100g', 'fat', 'Fat'),
                    (fiber_limit, 'fiber_100g', 'fiber', 'Fiber'),
                    (sugar_limit, 'sugars_100g', 'sugars', 'Sugar'),
                    (salt_limit, 'salt_100g', 'salt', 'Salt')
                ]
                
                for limit, key1, key2, name in limits:
                    if limit is not None:
                        value = nutriments.get(key1, nutriments.get(key2, None))
                        if value is not None and float(value) > limit:
                            return False, f"{name}: {value}g/100g (limit: {limit}g)"
                
                # Check protein limits separately (min and max)
                protein_value = nutriments.get('proteins_100g', nutriments.get('proteins', None))
                if protein_value is not None:
                    protein_value = float(protein_value)
                    if min_protein_limit is not None and protein_value < min_protein_limit:
                        return False, f"Protein: {protein_value}g/100g (minimum: {min_protein_limit}g)"
                    if max_protein_limit is not None and protein_value > max_protein_limit:
                        return False, f"Protein: {protein_value}g/100g (maximum: {max_protein_limit}g)"
                
                # Check minimum calorie limits
                if min_calorie_limit is not None:
                    calorie_value = nutriments.get('energy-kcal_100g', nutriments.get('energy-kcal', None))
                    if calorie_value is not None and float(calorie_value) < min_calorie_limit:
                        return False, f"Calories: {calorie_value} kcal/100g (minimum: {min_calorie_limit} kcal)"
                
                # Check minimum fiber limits
                if min_fiber_limit is not None:
                    fiber_value = nutriments.get('fiber_100g', nutriments.get('fiber', None))
                    if fiber_value is not None and float(fiber_value) < min_fiber_limit:
                        return False, f"Fiber: {fiber_value}g/100g (minimum: {min_fiber_limit}g)"
                
                return True, None
            
            for i, product in enumerate(products):
                total_checked += 1
                
                # First check nutrient filters if any are specified
                has_nutrient_filters = any([
                    filters['low_fat'], filters['low_fiber'], filters['low_sugar'], 
                    filters['low_salt'], filters['no_nuts'], calorie_limit is not None,
                    min_calorie_limit is not None, fat_limit is not None, 
                    fiber_limit is not None, min_fiber_limit is not None,
                    sugar_limit is not None, salt_limit is not None,
                    min_protein_limit is not None, max_protein_limit is not None
                ])
                
                if has_nutrient_filters:
                    meets_filters, filter_reason = meets_nutrient_filters(product)
                    if not meets_filters:
                        continue  # Skip products that don't meet nutrient filters
                
                product_name_result = product.get('product_name', 'Unknown Product')
                barcode = product.get('code', 'N/A')
                brand = product.get('brands', 'Unknown Brand')
                
                # Clean up the text
                product_name_result = ''.join(c for c in product_name_result if c.isprintable() and c.isascii()) if product_name_result else 'Unknown Product'
                brand = ''.join(c for c in brand if c.isprintable() and c.isascii()) if brand else 'Unknown Brand'
                
                # Analyze product safety against user profile
                is_safe, warnings, recommendations = analyze_product_safety(product)
                
                result_line = f"{len(filtered_results)+1}. **{product_name_result} ({brand})**\nhttps://world.openfoodfacts.org/product/{barcode}"
                
                # Add safety indicators
                if not is_safe:
                    result_line += " ❌ NOT SAFE"
                elif warnings:
                    result_line += " ⚠️ CAUTION"
                else:
                    result_line += " ✅ SAFE"
                
                # Add nutrient info if filters were applied
                if has_nutrient_filters:
                    nutriments = product.get('nutriments', {})
                    nutrient_info = []
                    if calorie_limit is not None:
                        calories = nutriments.get('energy-kcal_100g', nutriments.get('energy-kcal', 'N/A'))
                        if calories != 'N/A':
                            nutrient_info.append(f"{calories} kcal")
                    if min_calorie_limit is not None:
                        calories = nutriments.get('energy-kcal_100g', nutriments.get('energy-kcal', 'N/A'))
                        if calories != 'N/A':
                            nutrient_info.append(f"{calories} kcal")
                    if fat_limit is not None:
                        fat = nutriments.get('fat_100g', nutriments.get('fat', 'N/A'))
                        if fat != 'N/A':
                            nutrient_info.append(f"{fat}g fat")
                    if sugar_limit is not None:
                        sugar = nutriments.get('sugars_100g', nutriments.get('sugars', 'N/A'))
                        if sugar != 'N/A':
                            nutrient_info.append(f"{sugar}g sugar")
                    if salt_limit is not None:
                        salt = nutriments.get('salt_100g', nutriments.get('salt', 'N/A'))
                        if salt != 'N/A':
                            nutrient_info.append(f"{salt}g salt")
                    if fiber_limit is not None:
                        fiber = nutriments.get('fiber_100g', nutriments.get('fiber', 'N/A'))
                        if fiber != 'N/A':
                            nutrient_info.append(f"{fiber}g fiber")
                    if min_fiber_limit is not None:
                        fiber = nutriments.get('fiber_100g', nutriments.get('fiber', 'N/A'))
                        if fiber != 'N/A':
                            nutrient_info.append(f"{fiber}g fiber")
                    if min_protein_limit is not None or max_protein_limit is not None:
                        protein = nutriments.get('proteins_100g', nutriments.get('proteins', 'N/A'))
                        if protein != 'N/A':
                            nutrient_info.append(f"{protein}g protein")
                    
                    if nutrient_info:
                        result_line += f" | {', '.join(nutrient_info)}"
                
                filtered_results.append(result_line)
                
                # Collect warnings for summary
                if warnings:
                    profile_warnings.extend([f"Product {len(filtered_results)}: {w}" for w in warnings])
                
                # Stop after finding 10 results or checking 50 products
                if len(filtered_results) >= 10 or total_checked >= 50:
                    break
            
            
            # Generate response message
            if not filtered_results:
                if has_nutrient_filters:
                    filter_summary = []
                    if filters['low_fat'] or fat_limit is not None:
                        filter_summary.append(f"Low fat (≤{fat_limit}g)")
                    if filters['low_fiber'] or fiber_limit is not None:
                        filter_summary.append(f"Low fiber (≤{fiber_limit}g)")
                    if filters['low_sugar'] or sugar_limit is not None:
                        filter_summary.append(f"Low sugar (≤{sugar_limit}g)")
                    if filters['low_salt'] or salt_limit is not None:
                        filter_summary.append(f"Low salt (≤{salt_limit}g)")
                    if filters['no_nuts']:
                        filter_summary.append("No nuts")
                    if calorie_limit is not None:
                        filter_summary.append(f"≤{calorie_limit} calories")
                    if min_calorie_limit is not None:
                        filter_summary.append(f"≥{min_calorie_limit} calories")
                    if min_fiber_limit is not None:
                        filter_summary.append(f"≥{min_fiber_limit}g fiber")
                    if min_protein_limit is not None:
                        filter_summary.append(f"≥{min_protein_limit}g protein")
                    if max_protein_limit is not None:
                        filter_summary.append(f"≤{max_protein_limit}g protein")
                    
                    message = f"No products found for '{product_name}' matching your filters: {', '.join(filter_summary)}.\n"
                    message += f"Checked {total_checked} products. Try relaxing some filters or using different search terms."
                else:
                    message = f"No products found for '{product_name}'. Try a different search term."
            else:
                if has_nutrient_filters:
                    filter_summary = []
                    if filters['low_fat'] or fat_limit is not None:
                        filter_summary.append(f"Low fat (≤{fat_limit}g)")
                    if filters['low_fiber'] or fiber_limit is not None:
                        filter_summary.append(f"Low fiber (≤{fiber_limit}g)")
                    if filters['low_sugar'] or sugar_limit is not None:
                        filter_summary.append(f"Low sugar (≤{sugar_limit}g)")
                    if filters['low_salt'] or salt_limit is not None:
                        filter_summary.append(f"Low salt (≤{salt_limit}g)")
                    if filters['no_nuts']:
                        filter_summary.append("No nuts")
                    if calorie_limit is not None:
                        filter_summary.append(f"≤{calorie_limit} calories")
                    if min_calorie_limit is not None:
                        filter_summary.append(f"≥{min_calorie_limit} calories")
                    if min_fiber_limit is not None:
                        filter_summary.append(f"≥{min_fiber_limit}g fiber")
                    if min_protein_limit is not None:
                        filter_summary.append(f"≥{min_protein_limit}g protein")
                    if max_protein_limit is not None:
                        filter_summary.append(f"≤{max_protein_limit}g protein")
                    
                    message = f"Found {len(filtered_results)} products for '{product_name}' matching filters: {', '.join(filter_summary)}\n"
                    message += f"(Checked {total_checked} total products)\n\n"
                else:
                    message = f"Found {len(products)} products:\n"
                
                message += "\n".join(filtered_results)
                
                if has_nutrient_filters and len(filtered_results) < len(products):
                    filtered_out = len(products) - len(filtered_results)
                    message += f"\n\nℹ️ {filtered_out} products were filtered out due to nutrient criteria."
                elif not has_nutrient_filters and len(products) > len(filtered_results):
                    message += f"\n... and {len(products) - len(filtered_results)} more results."
            
            message += f"\n\nNote: These results are for reference only. Please check the actual product packaging for the most accurate information."
            
            # Add safety indicator explanation if user has a profile
            global USER_PROFILE
            if USER_PROFILE is not None:
                message += f"\n\n🛡️ SAFETY INDICATORS:\n✅ SAFE - No issues detected for your dietary profile\n⚠️ CAUTION - Contains ingredients you should be cautious about\n❌ NOT SAFE - Contains allergens or ingredients to avoid"
                
                # Check if any products are unsafe
                has_unsafe_products = any("❌ NOT SAFE" in result for result in filtered_results)
                if has_unsafe_products:
                    message += f"\n\n💡 TIP: Use 'search_safe_food_only' to see only products that are safe for your dietary profile."

            # Add profile warnings summary
            if profile_warnings:
                message += f"\n\n🔍 DIETARY ANALYSIS:\n" + "\n".join(profile_warnings[:10])  # Limit to 10 warnings
                if len(profile_warnings) > 10:
                    message += f"\n... and {len(profile_warnings) - 10} more warnings."
            
            logging.info(f"Product search successful for: {product_name}")
            return {
                "success": True,
                "message": message
            }
        else:
            logging.error(f"Failed to search products for: {product_name}. Status code: {response.status_code}")
            return {"success": False, "message": f"Failed to search products. Status code: {response.status_code}"}
    except requests.Timeout:
        logging.error(f"Timeout while searching products for: {product_name}")
        return {"success": False, "message": "Request timed out. Please try again."}
    except requests.RequestException as e:
        logging.error(f"Request error while searching products for: {product_name}. Error: {str(e)}")
        return {"success": False, "message": f"Error searching products: {str(e)}"}
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse search results for: {product_name}. Error: {str(e)}")
        return {"success": False, "message": "Failed to parse search results."}
    except Exception as e:
        logging.error(f"Unexpected error while searching products for: {product_name}. Error: {str(e)}")
        return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}

def get_product_nutrition(params: dict = None) -> dict:
    """Retrieve detailed nutritional information for a product by barcode."""
    if not params or "barcode" not in params:
        logging.error("Barcode parameter is required in get_product_nutrition")
        return {"success": False, "message": "Barcode parameter is required."}
    
    barcode = params["barcode"]
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            product_data = response.json()
            
            if product_data.get('status') != 1:
                logging.info(f"Product not found for barcode: {barcode}")
                return {
                    "success": False,
                    "message": f"Product with barcode '{barcode}' not found."
                }
            
            product = product_data.get('product', {})
            
            # Extract product information
            product_name = product.get('product_name', 'Unknown Product')
            brand = product.get('brands', 'Unknown Brand')
            
            # Extract nutritional information
            nutriments = product.get('nutriments', {})
            
            # Get key nutritional values (per 100g)
            energy_kcal = nutriments.get('energy-kcal_100g', nutriments.get('energy-kcal', 'N/A'))
            fat = nutriments.get('fat_100g', nutriments.get('fat', 'N/A'))
            sugar = nutriments.get('sugars_100g', nutriments.get('sugars', 'N/A'))
            protein = nutriments.get('proteins_100g', nutriments.get('proteins', 'N/A'))
            salt = nutriments.get('salt_100g', nutriments.get('salt', 'N/A'))
            fiber = nutriments.get('fiber_100g', nutriments.get('fiber', 'N/A'))
            
            # Clean up the text
            product_name = ''.join(c for c in product_name if c.isprintable() and c.isascii()) if product_name else 'Unknown Product'
            brand = ''.join(c for c in brand if c.isprintable() and c.isascii()) if brand else 'Unknown Brand'
            
            # Format the nutritional information
            nutrition_parts = []
            
            if energy_kcal != 'N/A':
                nutrition_parts.append(f"\n• Energy: {energy_kcal} kcal/100g")
            if fat != 'N/A':
                nutrition_parts.append(f"\n• Fat: {fat}g")
            if sugar != 'N/A':
                nutrition_parts.append(f"\n• Sugar: {sugar}g")
            if protein != 'N/A':
                nutrition_parts.append(f"\n• Protein: {protein}g")
            if salt != 'N/A':
                nutrition_parts.append(f"\n• Salt: {salt}g")
            if fiber != 'N/A':
                nutrition_parts.append(f"\n• Fiber: {fiber}g")
            
            if nutrition_parts:
                nutrition_info = ", ".join(nutrition_parts)
                message = f"**{product_name} ({brand})** {nutrition_info}"
            else:
                message = f"**{product_name} ({brand}): Nutritional information not available"
            
            # Add safety analysis based on user profile
            is_safe, warnings, recommendations = analyze_product_safety(product)
            
            if warnings or recommendations:
                message += "\n• 🔍 DIETARY ANALYSIS:"
                for warning in warnings:
                    message += f"\n• {warning}"
                for recommendation in recommendations:
                    message += f"\n• {recommendation}"
                
                if not is_safe:
                    message += "\n• ❌ This product is NOT RECOMMENDED for your dietary profile."
                elif warnings:
                    message += "\n• ⚠️ Please review the warnings above before consuming."
                else:
                    message += "\n• ✅ This product appears suitable for your dietary profile."
            
            logging.info(f"Nutritional data retrieved successfully for barcode: {barcode}")
            return {
                "success": True,
                "message": message
            }
        else:
            logging.error(f"Failed to retrieve product data for barcode: {barcode}. Status code: {response.status_code}")
            return {"success": False, "message": f"Failed to retrieve product data. Status code: {response.status_code}"}
    except requests.Timeout:
        logging.error(f"Timeout while retrieving product data for barcode: {barcode}")
        return {"success": False, "message": "Request timed out. Please try again."}
    except requests.RequestException as e:
        logging.error(f"Request error while retrieving product data for barcode: {barcode}. Error: {str(e)}")
        return {"success": False, "message": f"Error retrieving product data: {str(e)}"}
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse product data for barcode: {barcode}. Error: {str(e)}")
        return {"success": False, "message": "Failed to parse product data."}
    except Exception as e:
        logging.error(f"Unexpected error while retrieving product data for barcode: {barcode}. Error: {str(e)}")
        return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}

def set_user_profile(params: dict = None) -> dict:
    """Set the user's dietary profile for filtering food products."""
    global USER_PROFILE
    
    if not params:
        logging.error("Profile data is required in set_user_profile")
        return {"success": False, "message": "Profile data is required."}
    
    # Parse and validate parameters
    try:
        parsed_profile = {}
        
        # Parse each parameter with proper type checking
        parsed_profile["profile_name"] = params.get("profile_name", "Custom Profile")
        parsed_profile["allergies"] = safe_parse_parameter(params.get("allergies"), list)
        parsed_profile["intolerances"] = safe_parse_parameter(params.get("intolerances"), list)
        parsed_profile["medical_conditions"] = safe_parse_parameter(params.get("medical_conditions"), list)
        parsed_profile["dietary_preferences"] = safe_parse_parameter(params.get("dietary_preferences"), dict)
        parsed_profile["avoid_additives"] = safe_parse_parameter(params.get("avoid_additives"), list)
        parsed_profile["nutrient_limits"] = safe_parse_parameter(params.get("nutrient_limits"), dict)
        
        # Only add non-None values to the profile
        USER_PROFILE = {k: v for k, v in parsed_profile.items() if v is not None}
        
        profile_name = USER_PROFILE.get("profile_name", "Custom Profile")
        save_user_profile()
        
        logging.info(f"User profile set and saved: {profile_name}")
        return {
            "success": True,
            "message": f"Profile '{profile_name}' has been set and saved successfully. Dietary restrictions and preferences will now be applied to all food searches automatically."
        }
    except Exception as e:
        logging.error(f"Error setting user profile: {str(e)}")
        return {
            "success": False,
            "message": f"Error setting user profile: {str(e)}"
        }

def get_user_profile(params: dict = None) -> dict:
    """Get the current user profile settings."""
    global USER_PROFILE
    
    if USER_PROFILE is None:
        return {
            "success": True,
            "message": "No user profile is currently set. Use set_user_profile to configure dietary restrictions and preferences."
        }
    
    profile_name = USER_PROFILE.get("profile_name", "Custom Profile")
    allergies = USER_PROFILE.get("allergies", [])
    intolerances = USER_PROFILE.get("intolerances", [])
    medical_conditions = USER_PROFILE.get("medical_conditions", [])
    dietary_preferences = USER_PROFILE.get("dietary_preferences", {})
    avoid_additives = USER_PROFILE.get("avoid_additives", [])
    nutrient_limits = USER_PROFILE.get("nutrient_limits", {})
    
    summary = f"📋 Current Profile: {profile_name}"
    
    if allergies:
        summary += f"\n🚨 Allergies: {', '.join(allergies)}"
    if intolerances:
        summary += f"\n⚠️ Intolerances: {', '.join(intolerances)}"
    if medical_conditions:
        summary += f"\n🏥 Medical Conditions: {', '.join(medical_conditions)}"
    
    if dietary_preferences and isinstance(dietary_preferences, dict):
        active_prefs = [k for k, v in dietary_preferences.items() if v]
        if active_prefs:
            summary += f"\n🥗 Dietary Preferences: {', '.join(active_prefs)}"
    
    if avoid_additives and isinstance(avoid_additives, list):
        summary += f"\n🧪 Avoid Additives: {', '.join(avoid_additives)}"
    
    if nutrient_limits and isinstance(nutrient_limits, dict):
        limits = [f"{nutrient}: {limit}" for nutrient, limit in nutrient_limits.items()]
        if limits:
            summary += f"\n📊 Nutrient Limits: {', '.join(limits)}"
    
    summary += "\n\n✅ This profile is automatically applied to all food searches."
    
    return {"success": True, "message": summary, "profile_data": USER_PROFILE}

def clear_user_profile(params: dict = None) -> dict:
    """Clear the current user profile and remove the saved profile file."""
    global USER_PROFILE, PROFILE_FILE
    
    USER_PROFILE = None
    
    try:
        if os.path.exists(PROFILE_FILE):
            os.remove(PROFILE_FILE)
            logging.info("User profile file deleted")
    except Exception as e:
        logging.error(f"Failed to delete profile file: {str(e)}")
    
    logging.info("User profile cleared")
    return {
        "success": True,
        "message": "User profile has been cleared successfully. No dietary restrictions will be applied to future searches until a new profile is set."
    }

def analyze_product_safety(product_data: dict, strict_mode: bool = False) -> tuple:
    """
    Analyze a product against the user's profile for safety warnings.
    
    Args:
        product_data: Product data from Open Food Facts API
        strict_mode: If True, filter out ANY products with unknown vegan/vegetarian status
        
    Returns:
        tuple: (is_safe: bool, warnings: list, recommendations: list)
    """
    global USER_PROFILE
    
    if USER_PROFILE is None:
        return True, [], []
    
    warnings = []
    recommendations = []
    is_safe = True
    
    # Check allergies
    allergies = USER_PROFILE.get("allergies", [])
    allergens = product_data.get("allergens_tags", [])
    ingredients_text = product_data.get("ingredients_text", "").lower()
    
    for allergy in allergies:
        allergy_lower = allergy.lower()
        
        # Enhanced nuts detection
        if allergy_lower in ['nuts', 'nut', 'tree nuts']:
            nuts_keywords = [
                'nuts', 'nut', 'almond', 'walnut', 'peanut', 'cashew', 
                'pistachio', 'hazelnut', 'pecan', 'macadamia', 'brazil nut',
                'pine nut', 'chestnut', 'beechnut', 'hickory nut', 
                'may contain nuts', 'may contain nut', 'tree nuts'
            ]
            
            # Check allergens tags for nut-related allergens
            has_nut_allergen = any('nut' in allergen.lower() for allergen in allergens)
            
            # Check ingredients text for nut keywords
            has_nut_ingredient = any(nut in ingredients_text for nut in nuts_keywords)
            
            # Check additional fields where nuts might be mentioned, but be smart about percentages
            additional_fields_to_check = [
                product_data.get('product_name', '').lower(),
                product_data.get('generic_name', '').lower(),
                product_data.get('categories', '').lower(),
                product_data.get('labels', '').lower(),
                product_data.get('traces', '').lower(),
                product_data.get('ingredients_analysis_tags', []),
                product_data.get('categories_tags', []),
                product_data.get('labels_tags', [])
            ]
            
            # Check nutriments field more carefully for percentage values
            nutriments_str = str(product_data.get('nutriments', {})).lower()
            has_nut_in_nutriments = False
            if any(nut in nutriments_str for nut in nuts_keywords):
                # Found nuts keywords in nutriments, now check if percentage is > 0
                import re
                # Look for patterns like "nuts...X%" where X is the percentage
                # Match the entire phrase containing nuts and extract the percentage
                nuts_percentage_matches = re.findall(r'[^{}\'"]*(?:nuts|nut|walnut|almond|peanut|cashew|pistachio|hazelnut|pecan|macadamia)[^{}\'"]*?(\d+(?:\.\d+)?)\s*%', nutriments_str, re.IGNORECASE)
                
                if nuts_percentage_matches:
                    # Check if any percentage is > 0
                    for percentage_str in nuts_percentage_matches:
                        try:
                            percentage = float(percentage_str)
                            if percentage > 0:
                                has_nut_in_nutriments = True
                                break
                        except ValueError:
                            continue
                else:
                    # If no percentage pattern found but nuts keyword exists, check if it's a general mention
                    # But be conservative - don't flag unless we're sure
                    if any(phrase in nutriments_str for phrase in ['may contain nuts', 'may contain nut', 'contains nuts', 'contains nut']):
                        has_nut_in_nutriments = True
            
            # Check all other additional fields for nuts keywords (excluding nutriments which we handled above)
            has_nut_in_additional_fields = False
            for field in additional_fields_to_check:
                if isinstance(field, str):
                    if any(nut in field for nut in nuts_keywords):
                        has_nut_in_additional_fields = True
                        break
                elif isinstance(field, list):
                    if any(any(nut in str(item).lower() for nut in nuts_keywords) for item in field):
                        has_nut_in_additional_fields = True
                        break
            
            if has_nut_allergen or has_nut_ingredient or has_nut_in_nutriments or has_nut_in_additional_fields:
                warnings.append(f"⚠️ ALLERGY WARNING: Contains {allergy}")
                is_safe = False
                
        else:
            # Standard allergy checking for other allergens
            if any(allergy_lower in allergen.lower() for allergen in allergens) or allergy_lower in ingredients_text:
                warnings.append(f"⚠️ ALLERGY WARNING: Contains {allergy}")
                is_safe = False
    
    # Check intolerances
    intolerances = USER_PROFILE.get("intolerances", [])
    for intolerance in intolerances:
        intolerance_lower = intolerance.lower()
        if intolerance_lower in ingredients_text:
            warnings.append(f"⚠️ INTOLERANCE WARNING: May contain {intolerance}")
            if strict_mode:
                is_safe = False
    
    # Check nutrient limits
    nutrient_limits = USER_PROFILE.get("nutrient_limits", {})
    nutriments = product_data.get("nutriments", {})
    
    if isinstance(nutrient_limits, dict):
        for nutrient, limit in nutrient_limits.items():
            value = nutriments.get(nutrient, nutriments.get(nutrient.replace("_100g", ""), 0))
            if isinstance(value, (int, float)) and value > limit:
                warnings.append(f"⚠️ HIGH {nutrient.replace('_100g', '').upper()}: {value}g (limit: {limit}g)")
                if strict_mode:
                    is_safe = False
    
    # Check dietary preferences
    dietary_prefs = USER_PROFILE.get("dietary_preferences", {})
    
    # Helper function for vegan/vegetarian checking
    def check_diet_status(diet_type, non_diet_indicators):
        diet_labels = product_data.get("labels_tags", [])
        is_explicitly_labeled = any(diet_type in label.lower() for label in diet_labels)
        
        if f"{diet_type} status unknown" in ingredients_text.lower():
            warnings.append(f"⚠️ {diet_type.upper()} STATUS UNKNOWN: Product explicitly states unknown {diet_type} status")
            return False
        elif is_explicitly_labeled:
            return True
        else:
            found_non_diet = False
            for indicator in non_diet_indicators:
                if indicator in ingredients_text.lower():
                    warnings.append(f"⚠️ NOT {diet_type.upper()}: Contains {indicator}")
                    found_non_diet = True
                    return False
            
            if not found_non_diet and (not ingredients_text or len(ingredients_text.strip()) < 20):
                warnings.append(f"⚠️ {diet_type.upper()} STATUS UNKNOWN: Insufficient ingredient information" + (" - FILTERED OUT" if strict_mode else ""))
                return False if strict_mode else True
            
            return True
    
    if dietary_prefs.get("vegan", False):
        non_vegan_indicators = ["milk", "egg", "meat", "fish", "honey", "gelatin", "whey", "casein", "dairy", "cheese", "butter", "cream", "lactose", "chicken", "beef", "pork", "bacon", "lard"]
        if not check_diet_status("vegan", non_vegan_indicators):
            is_safe = False

    if dietary_prefs.get("vegetarian", False):
        non_vegetarian_indicators = ["meat", "fish", "chicken", "beef", "pork", "bacon", "lard", "gelatin", "anchovies", "tuna", "salmon", "cod"]
        if not check_diet_status("vegetarian", non_vegetarian_indicators):
            is_safe = False
    
    # Check avoided additives
    avoid_additives = USER_PROFILE.get("avoid_additives", [])
    additives = product_data.get("additives_tags", [])
    
    for additive in avoid_additives:
        if any(additive.lower() in tag.lower() for tag in additives):
            warnings.append(f"⚠️ CONTAINS AVOIDED ADDITIVE: {additive}")
            if strict_mode:
                is_safe = False
    
    # Generate recommendations
    if dietary_prefs.get("low_sugar", False) and nutriments.get("sugars_100g", 0) > 5:
        recommendations.append("💡 Consider a low-sugar alternative")
    
    if dietary_prefs.get("low_salt", False) and nutriments.get("salt_100g", 0) > 1.5:
        recommendations.append("💡 Consider a low-salt alternative")
    
    return is_safe, warnings, recommendations

def search_vegan_products(product_name: str) -> list:
    """
    Search specifically for vegan products using Open Food Facts vegan label filter.
    Only returns products that actually contain "vegan" in their labels field.
    
    Args:
        product_name (str): The product name to search for
        
    Returns:
        list: List of products that are explicitly labeled as vegan
    """
    try:
        # First try direct vegan label search
        formatted_name = product_name.replace(" ", "+")
        # Use the v1 search API with vegan label filter
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={formatted_name}&tagtype_0=labels&tag_contains_0=contains&tag_0=vegan&search_simple=1&action=process&json=1"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            search_data = response.json()
            products = search_data.get('products', [])
            
            # FILTER: Only return products that actually have "vegan" in their labels
            vegan_products = []
            for product in products:
                labels = product.get('labels', '').lower()
                if 'vegan' in labels:
                    vegan_products.append(product)
            
            if vegan_products:
                logging.info(f"Found {len(vegan_products)} verified vegan-labeled products for: {product_name}")
                return vegan_products
        
        # Fallback: try using the direct URL approach
        url = f"https://world.openfoodfacts.org/label/vegan/search/{formatted_name}.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            search_data = response.json()
            products = search_data.get('products', [])
            
            # FILTER: Only return products that actually have "vegan" in their labels
            vegan_products = []
            for product in products:
                labels = product.get('labels', '').lower()
                if 'vegan' in labels:
                    vegan_products.append(product)
            
            if vegan_products:
                logging.info(f"Found {len(vegan_products)} verified vegan products via label URL for: {product_name}")
                return vegan_products
                
    except Exception as e:
        logging.warning(f"Error in vegan-specific search for {product_name}: {str(e)}")
    
    return []

def search_vegetarian_products(product_name: str) -> list:
    """
    Search specifically for vegetarian products using Open Food Facts vegetarian label filter.
    Only returns products that actually contain "vegetarian" in their labels field.
    
    Args:
        product_name (str): The product name to search for
        
    Returns:
        list: List of products that are explicitly labeled as vegetarian
    """
    try:
        # First try direct vegetarian label search
        formatted_name = product_name.replace(" ", "+")
        # Use the v1 search API with vegetarian label filter
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={formatted_name}&tagtype_0=labels&tag_contains_0=contains&tag_0=vegetarian&search_simple=1&action=process&json=1"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            search_data = response.json()
            products = search_data.get('products', [])
            
            # FILTER: Only return products that actually have "vegetarian" in their labels
            vegetarian_products = []
            for product in products:
                labels = product.get('labels', '').lower()
                if 'vegetarian' in labels:
                    vegetarian_products.append(product)
            
            if vegetarian_products:
                logging.info(f"Found {len(vegetarian_products)} verified vegetarian-labeled products for: {product_name}")
                return vegetarian_products
        
        # Fallback: try using the direct URL approach
        url = f"https://world.openfoodfacts.org/label/vegetarian/search/{formatted_name}.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            search_data = response.json()
            products = search_data.get('products', [])
            
            # FILTER: Only return products that actually have "vegetarian" in their labels
            vegetarian_products = []
            for product in products:
                labels = product.get('labels', '').lower()
                if 'vegetarian' in labels:
                    vegetarian_products.append(product)
            
            if vegetarian_products:
                logging.info(f"Found {len(vegetarian_products)} verified vegetarian products via label URL for: {product_name}")
                return vegetarian_products
                
    except Exception as e:
        logging.warning(f"Error in vegetarian-specific search for {product_name}: {str(e)}")
    
    return []

def search_safe_food_only(params: dict = None) -> dict:
    """
    Searches for food products by name and returns ONLY products that are safe for the user's dietary profile.
    Uses enhanced search with Open Food Facts API filters when possible.
    
    Args:
        params (dict, optional): Dictionary containing parameters. Must include 'product_name' key.
            Example: {"product_name": "coca cola"}
        
    Returns:
        dict: A dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Safe products only or error message
           
            
    Example:
        >>> search_safe_food_only({"product_name": "bread"})
        {
            "success": True,
            "message": "Found 3 SAFE products: Gluten-Free Bread (✅), Vegan Bread (✅), ..."
           
        }
    """
    global USER_PROFILE
    
    if not params or "product_name" not in params:
        logging.error("Product name parameter is required in search_safe_food_only")
        return {"success": False, "message": "Product name parameter is required."}
    
    if USER_PROFILE is None:
        return {
            "success": False, 
            "message": "No dietary profile set. Please set your dietary profile first to filter safe foods. Use set_user_profile command to configure your dietary restrictions and preferences."
        }
    
    product_name = params["product_name"]
    
    # Try enhanced search with API filters first if user is vegan or vegetarian
    dietary_prefs = USER_PROFILE.get("dietary_preferences", {})
    safe_products = []
    safe_product_barcodes = []  # Track barcodes for URL generation
    total_checked = 0
    
    # If user is vegan, try to search specifically for vegan products first
    if dietary_prefs.get("vegan", False):
        vegan_products = search_vegan_products(product_name)
        if vegan_products:
            for product in vegan_products[:10]:
                total_checked += 1
                is_safe, warnings, recommendations = analyze_product_safety(product, strict_mode=True)
                
                # STRICT: Only include products that are completely safe with NO warnings
                if is_safe and not warnings:
                    product_name_result = product.get('product_name', 'Unknown Product')
                    barcode = product.get('code', 'N/A')
                    brand = product.get('brands', 'Unknown Brand')
                    
                    # Clean up the text
                    product_name_result = ''.join(c for c in product_name_result if c.isprintable() and c.isascii()) if product_name_result else 'Unknown Product'
                    brand = ''.join(c for c in brand if c.isprintable() and c.isascii()) if brand else 'Unknown Brand'
                    
                    result_line = f"{len(safe_products)+1}. **{product_name_result} ({brand})**\nhttps://world.openfoodfacts.org/product/{barcode} ✅ VEGAN SAFE"
                    safe_products.append(result_line)
                    safe_product_barcodes.append(barcode)
                    
                    if len(safe_products) >= 10:
                        break
    
    # If user is vegetarian (and not vegan), try to search specifically for vegetarian products
    elif dietary_prefs.get("vegetarian", False):
        vegetarian_products = search_vegetarian_products(product_name)
        if vegetarian_products:
            for product in vegetarian_products[:10]:
                total_checked += 1
                is_safe, warnings, recommendations = analyze_product_safety(product, strict_mode=True)
                
                # STRICT: Only include products that are completely safe with NO warnings
                if is_safe and not warnings:
                    product_name_result = product.get('product_name', 'Unknown Product')
                    barcode = product.get('code', 'N/A')
                    brand = product.get('brands', 'Unknown Brand')
                    
                    # Clean up the text
                    product_name_result = ''.join(c for c in product_name_result if c.isprintable() and c.isascii()) if product_name_result else 'Unknown Product'
                    brand = ''.join(c for c in brand if c.isprintable() and c.isascii()) if brand else 'Unknown Brand'
                    
                    result_line = f"{len(safe_products)+1}. **{product_name_result} ({brand})**\nhttps://world.openfoodfacts.org/product/{barcode} ✅ VEGETARIAN SAFE"
                    safe_products.append(result_line)
                    safe_product_barcodes.append(barcode)
                    
                    if len(safe_products) >= 10:
                        break
    
    # If we didn't find enough products with vegan-specific search, do general search
    if len(safe_products) < 5:
        formatted_name = product_name.replace(" ", "+")
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={formatted_name}&search_simple=1&action=process&json=1"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                search_data = response.json()
                products = search_data.get('products', [])
                
                for product in products[:20]:  # Check more products to find safe ones
                    if total_checked >= 20:  # Limit total products checked
                        break
                    total_checked += 1
                    
                    # STRICT analysis - filter out ANY products with unknown status
                    is_safe, warnings, recommendations = analyze_product_safety(product, strict_mode=True)
                    
                    # STRICT: Only include products that are completely safe (no warnings at all)
                    if is_safe and not warnings:
                        product_name_result = product.get('product_name', 'Unknown Product')
                        barcode = product.get('code', 'N/A')
                        brand = product.get('brands', 'Unknown Brand')
                        
                        # Clean up the text
                        product_name_result = ''.join(c for c in product_name_result if c.isprintable() and c.isascii()) if product_name_result else 'Unknown Product'
                        brand = ''.join(c for c in brand if c.isprintable() and c.isascii()) if brand else 'Unknown Brand'
                        
                        result_line = f"{len(safe_products)+1}. **{product_name_result} ({brand})**\nhttps://world.openfoodfacts.org/product/{barcode} ✅ SAFE"
                        safe_products.append(result_line)
                        safe_product_barcodes.append(barcode)
                        
                        # Stop after finding 10 safe products
                        if len(safe_products) >= 10:
                            break
        
        except requests.RequestException as e:
            logging.error(f"Error searching for products: {str(e)}")
            return {"success": False, "message": f"Error searching for products: {str(e)}"}
    
    if not safe_products:
        message = f"❌ No completely safe products found for '{product_name}' using STRICT filtering.\n\n"
        message += f"Checked {total_checked} products. All were filtered out due to:\n"
        message += f"• Allergen conflicts\n• Unknown vegan/vegetarian status\n• Nutrient limit violations\n• Missing critical information\n\n"
        
        # Remind user of their restrictions
        allergies = USER_PROFILE.get("allergies", [])
        intolerances = USER_PROFILE.get("intolerances", [])
        dietary_prefs = USER_PROFILE.get("dietary_preferences", {})
        
        if allergies:
            message += f"🚨 Allergies to avoid: {', '.join(allergies)}\n"
        if intolerances:
            message += f"⚠️ Intolerances: {', '.join(intolerances)}\n"
        if dietary_prefs.get("vegan"):
            message += f"🥗 Vegan requirement (strict - excludes unknown status)\n"
        if dietary_prefs.get("vegetarian"):
            message += f"🥛 Vegetarian requirement (strict - excludes unknown status)\n"
        
        message += f"\n💡 Try: \n- Use regular search to see products with warnings\n- Try different/broader search terms\n- Use analyze_product to check specific barcodes\n- Consider adjusting your dietary profile if needed"
        
        message += f"\n\nNote: These results are for reference only. Please check the actual product packaging for the most accurate information."


        logging.info(f"No safe products found for: {product_name}")
        return {
            "success": True,
            "message": message
        }
    
    message = f"🎯 Found {len(safe_products)} SAFE products for '{product_name}' (checked {total_checked} total):\n\n"
    message += "\n".join(safe_products)
    
    if len(safe_products) == 10:
        message += f"\n\n📝 Showing first 10 safe results. There may be more safe options available."
    
    message += f"\n\n• All listed products meet your dietary requirements:\n"
    
    # Show what requirements were checked
    profile_summary = []
    allergies = USER_PROFILE.get("allergies", [])
    intolerances = USER_PROFILE.get("intolerances", [])
    dietary_prefs = USER_PROFILE.get("dietary_preferences", {})
    nutrient_limits = USER_PROFILE.get("nutrient_limits", {})
    
    if allergies:
        profile_summary.append(f"No {', '.join(allergies)} allergens")
    if intolerances:
        profile_summary.append(f"No {', '.join(intolerances)}")
    if dietary_prefs.get("vegan"):
        profile_summary.append("Vegan-friendly")
    if dietary_prefs.get("vegetarian"):
        profile_summary.append("Vegetarian-friendly")
    if nutrient_limits and isinstance(nutrient_limits, dict):
        limits_text = []
        for nutrient, limit in nutrient_limits.items():
            nutrient_clean = nutrient.replace("_100g", "")
            limits_text.append(f"{nutrient_clean} ≤ {limit}g")
        if limits_text:
            profile_summary.append(f"Within limits: {', '.join(limits_text)}")
    
    if profile_summary:
        message += "✅ " + "\n".join(profile_summary)
    
    message += f"\n\nNote: These results are for reference only. Please check the actual product packaging for the most accurate information."
    
    # Generate URL for the first safe product (if any)
    response_dict = {
        "success": True,
        "message": message
    }
    
    # Try to get URL from collected barcodes first
    if safe_product_barcodes and safe_product_barcodes[0] != 'N/A':
        first_barcode = safe_product_barcodes[0]
        response_dict["url"] = f"https://world.openfoodfacts.org/product/{first_barcode}"
    # Fallback: extract barcode from the first product in the message
    elif safe_products:
        # Extract barcode from first product line (format: "Barcode: XXXXXXXXX")
        first_product = safe_products[0]
        barcode_match = re.search(r'Barcode: (\w+)', first_product)
        if barcode_match:
            first_barcode = barcode_match.group(1)
            if first_barcode != 'N/A':
                response_dict["url"] = f"https://world.openfoodfacts.org/product/{first_barcode}"
    
    logging.info(f"Safe products search successful for: {product_name}, found {len(safe_products)} safe products")
    return response_dict

def main():
    """Main entry point for the DietCheck plugin. Handles command processing and maintains the event loop."""
    # Load saved user profile automatically on startup
    load_user_profile()
    
    commands = {
        'initialize': lambda _: {"success": True, "message": "DietCheck plugin initialized"},
        'shutdown': lambda _: {"success": True, "message": "DietCheck plugin shutdown"},
        'search_food_product': search_food_product,
        'get_product_nutrition': get_product_nutrition,
        'set_user_profile': set_user_profile,
        'get_user_profile': get_user_profile,
        'clear_user_profile': clear_user_profile,
        'search_safe_food_only': search_safe_food_only,
    }
    
    while True:
        command = read_command()
        if command is None:
            logging.error('Error reading command - skipping and continuing')
            # Send an error response to prevent the caller from hanging
            error_response = {"success": False, "message": "Failed to parse command"}
            write_response(error_response)
            continue
        
        tool_calls = command.get("tool_calls", [])
        for tool_call in tool_calls:
            logging.info(f"Tool call: {tool_call}")
            func = tool_call.get("func")
            logging.info(f"Function: {func}")
            params = tool_call.get("params", {})
            logging.info(f"Params: {params}")
            
            if func == 'initialize':
                response = commands.get('initialize')(params)
            elif func == 'search_food_product':
                logging.info(f"Searching food products for {params}")
                response = search_food_product(params)
                logging.info(f"Search result: {response}")
            elif func == 'get_product_nutrition':
                logging.info(f"Getting nutrition info for {params}")
                response = get_product_nutrition(params)
                logging.info(f"Nutrition info: {response}")
            elif func == 'set_user_profile':
                logging.info(f"Setting user profile: {params}")
                response = set_user_profile(params)
                logging.info(f"Profile set result: {response}")
            elif func == 'get_user_profile':
                logging.info("Getting user profile")
                response = get_user_profile(params)
                logging.info(f"Profile info: {response}")
            elif func == 'clear_user_profile':
                logging.info("Clearing user profile")
                response = clear_user_profile(params)
                logging.info(f"Profile clear result: {response}")
            elif func == 'search_safe_food_only':
                logging.info(f"Searching safe food only for {params}")
                response = search_safe_food_only(params)
                logging.info(f"Safe search result: {response}")
            elif func == 'shutdown':
                response = commands.get('shutdown')(params)
                write_response(response)
                return
            else:
                response = {'success': False, 'message': "Unknown function call"}
            
            write_response(response)
    
def read_command() -> dict | None:
    """Read a command from the communication pipe."""
    try:
        STD_INPUT_HANDLE = -10
        pipe = windll.kernel32.GetStdHandle(STD_INPUT_HANDLE)

        chunks = []
        while True:
            BUFFER_SIZE = 4096
            message_bytes = wintypes.DWORD()
            buffer = bytes(BUFFER_SIZE)
            success = windll.kernel32.ReadFile(pipe, buffer, BUFFER_SIZE, byref(message_bytes), None)

            if not success:
                logging.error('Error reading from command pipe')
                return None
            
            chunk = buffer.decode('utf-8')[:message_bytes.value]
            chunks.append(chunk)

            if message_bytes.value < BUFFER_SIZE:
                break

        retval = ''.join(chunks)
        
        # Clean up the JSON string before parsing
        retval = retval.strip()
        
        # Handle potential multiple JSON objects concatenated together
        def extract_first_json(data):
            """Extract the first complete JSON object from potentially concatenated data"""
            if not data:
                return None
                
            brace_count = 0
            in_string = False
            escape_next = False
            
            for i, char in enumerate(data):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\' and in_string:
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # Found the end of the first JSON object
                            return data[:i+1]
            
            # If we didn't find a complete JSON object, return the whole string
            return data
        
        # Extract only the first JSON object if multiple are present
        first_json = extract_first_json(retval)
        if first_json != retval:
            logging.warning(f'Multiple JSON objects detected, extracted first one. Original length: {len(retval)}, extracted: {len(first_json)}')
        
        # Try to parse the JSON with better error handling
        try:
            return json.loads(first_json)
        except json.JSONDecodeError as json_err:
            # Log first 500 characters of problematic JSON for debugging
            json_preview = first_json[:500] + "..." if len(first_json) > 500 else first_json
            logging.error(f'JSON decode error at position {json_err.pos}: {json_err.msg}')
            logging.error(f'Received invalid JSON (first 500 chars): {json_preview}')
            
            # Try to fix common JSON issues
            try:
                import re
                cleaned_json = first_json
                
                # Fix unescaped newlines within JSON string values
                # This pattern looks for unescaped newlines that are inside quotes
                def fix_newlines_in_strings(match):
                    content = match.group(1)
                    # Replace unescaped newlines with \\n
                    content = content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    return f'"{content}"'
                
                # Find all string values in the JSON and fix newlines within them
                cleaned_json = re.sub(r'"([^"]*(?:\\.[^"]*)*)"', fix_newlines_in_strings, cleaned_json)
                
                return json.loads(cleaned_json)
            except Exception as e:
                logging.error(f'Failed to clean and parse JSON: {str(e)}')
                return None

    except Exception as e:
        logging.error(f'Exception in read_command(): {str(e)}')
        return None


def write_response(response: Response) -> None:
    """Write a response to the communication pipe."""
    try:
        STD_OUTPUT_HANDLE = -11
        pipe = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

        # Use ensure_ascii=False to preserve Unicode characters like emojis
        json_message = json.dumps(response, ensure_ascii=False) + '<<END>>'
        message_bytes = json_message.encode('utf-8')
        message_len = len(message_bytes)

        bytes_written = wintypes.DWORD()
        success = windll.kernel32.WriteFile(pipe, message_bytes, message_len, bytes_written, None)

        if not success:
            logging.error('Error writing to response pipe')

    except Exception as e:
        logging.error(f'Exception in write_response(): {str(e)}')

if __name__ == "__main__":
    main()
