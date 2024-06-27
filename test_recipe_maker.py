import unittest
from unittest.mock import patch, MagicMock, mock_open
import recipe_maker


class TestRecipeMaker(unittest.TestCase):
    @patch('recipe_maker.input', create=True)
    def test_input_ingredients(self, mocked_input):
        mocked_input.side_effect = ["3", "salmon", "lemon", "dill"]
        result = recipe_maker.input_ingredients()
        self.assertEqual(result, "salmon,lemon,dill")
        print("Passed Ingredient Input Test")


    @patch('recipe_maker.input_ingredients')
    @patch('recipe_maker.requests.get')
    def test_fetch_recipes(self, mock_get, mock_input_ingredients):
        # Setup
        mock_input_ingredients.return_value = "salmon, lemon, dill"
        api_response = {
            "json.return_value": [
                {
                    "title": "Pan Seared Salmon",
                    "image": """https://img.spoonacular.com/recipes/
                        654435-312x231.jpg""",
                    "usedIngredients": [
                        {"name": "dill", "amount": 1.0, "unit": "tbsp"},
                        {"name": "lemon wedges", "amount": 2.0, "unit": 
                            "servings"},
                        {"name": "salmon fillets", "amount": 12.0, "unit": 
                            "oz"}
                    ],
                    "missedIngredients": [
                        {"name": "garlic clove", "amount": 1.0, "unit": ""},
                        {"name": "lemon juice", "amount": 1.0, "unit": "tbsp"}
                    ],
                    "missedIngredientCount": 2
                }
            ]
        }
        mock_get.return_value = MagicMock(**api_response)

        result = recipe_maker.fetch_recipes()

        expected_output = [
            '''Title: Pan Seared Salmon\nImage: 
                https://img.spoonacular.com/recipes/654435-312x231.jpg\nUsed
                 Ingredients:\n  - dill:\n            
                 1.0 tbsp\n  - lemon wedges:\n            
                 2.0 servings\n  - salmon fillets:\n            
                 12.0 oz\nMissed Ingredients\n        
                 (2):\n  - garlic clove:\n            
                 1.0 \n  - lemon juice:\n            
                 1.0 tbsp\n'''
        ]
        self.assertEqual(result, expected_output)
        print("Passed Fetch Recipe Test")


    @patch("builtins.open", new_callable=mock_open)
    @patch("builtins.print")
    def test_redirect_output(self, mock_print, mock_file_open):
        markdown_content = "Test content for Markdown file."

        recipe_maker.redirect_output(markdown_content)

        mock_file_open.assert_called_once_with("Recipe2.md", "w")
        mock_file_open().write.assert_called_once_with(markdown_content)

        mock_print.assert_called_once_with("""Markdown file 
            created successfully.""")
        print("Passed New Markdown File Test")


if __name__ == '__main__':
    unittest.main()
