"""
Test script to verify Gemini Vision API is working
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.vision import VisionModule
from agent.config import config


async def test_vision_api():
    """Test if the vision API is working"""
    
    print("=" * 60)
    print("🔍 Testing Vision API Configuration")
    print("=" * 60)
    
    # Check API keys
    print(f"\n1️⃣ API Keys Check:")
    print(f"   - Gemini API Keys: {len(config.gemini_api_keys)} configured")
    print(f"   - Current Key: {config.get_current_api_key()[:20]}..." if config.get_current_api_key() else "   - No key found")
    
    if not config.gemini_api_keys:
        print("\n❌ ERROR: No Gemini API keys configured!")
        print("   Please set GEMINI_API_KEY in your .env file")
        print("   Get a free key at: https://aistudio.google.com/app/apikey")
        return False
    
    # Initialize vision module
    print(f"\n2️⃣ Vision Module Initialization:")
    vision = VisionModule()
    
    if not vision.client:
        print("   ❌ Failed to initialize Vision Module")
        return False
    
    print(f"   ✅ Vision Module initialized")
    print(f"   - Model: {vision.current_model_name}")
    
    # Test with a simple image
    print(f"\n3️⃣ Testing API Call:")
    print("   Creating test image...")
    
    # Create a simple test image (1x1 white pixel PNG)
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    import base64
    test_image_bytes = base64.b64decode(test_image_base64)
    
    # Use the correct model name for google-genai v1beta API
    model_name = "gemini-3-flash-preview"
    print(f"   Using model: {model_name}")
    print("   Calling Gemini Vision API...")
    
    # Try with all available API keys
    for i, api_key in enumerate(config.gemini_api_keys, 1):
        try:
            from google.genai import types
            from google import genai
            
            # Test with this specific key
            test_client = genai.Client(api_key=api_key)
            
            print(f"   Trying API key #{i}...")
            
            response = test_client.models.generate_content(
                model=model_name,
                contents=[
                    types.Content(
                        parts=[
                            types.Part.from_text(text="What color is this image? Reply in one word."),
                            types.Part.from_bytes(data=test_image_bytes, mime_type="image/png")
                        ]
                    )
                ]
            )
        
            result_text = response.text.strip().lower()
            print(f"   ✅ API Response received from key #{i}: '{result_text}'")
            
            # Validate response
            if result_text:
                print("\n4️⃣ API Test Result:")
                print(f"   ✅ SUCCESS! Vision API is working correctly (using API key #{i})")
                print(f"   - Model responded with: {result_text}")
                return True
            else:
                print(f"   ⚠️ API key #{i} responded but returned empty text")
                continue
                
        except Exception as e:
            print(f"   ❌ API key #{i} failed: {str(e)[:100]}")
            
            # Check if this is the last key
            if i == len(config.gemini_api_keys):
                # This was the last key, show detailed error
                error_str = str(e).lower()
                if "429" in str(e) or "quota" in error_str or "rate" in error_str:
                    print("\n   💡 All API keys have exceeded quota.")
                    print("      - Wait a few minutes and try again")
                    print("      - Or check your usage at: https://ai.dev/usage")
                elif "401" in str(e) or "403" in str(e) or "invalid" in error_str:
                    print("\n   💡 API key authentication failed.")
                    print("      - Check your GEMINI_API_KEY in .env file")
                    print("      - Generate new keys at: https://aistudio.google.com/app/apikey")
                
                return False
            else:
                # Try next key
                continue
    
    print("\n4️⃣ API Test Result:")
    print("   ❌ All API keys failed")
    return False


def main():
    """Run the test"""
    try:
        result = asyncio.run(test_vision_api())
        
        print("\n" + "=" * 60)
        if result:
            print("✅ VISION API TEST PASSED")
            print("Your image model is working correctly!")
        else:
            print("❌ VISION API TEST FAILED")
            print("Please check the errors above and fix configuration")
        print("=" * 60 + "\n")
        
        sys.exit(0 if result else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
