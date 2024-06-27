import unittest
from unittest.mock import patch
import recipe_maker


class TestRecipeMaker(unittest.TestCase):
    @patch('recipe_maker.input', create=True)
    def test_input_ingredients(self, mocked_input):
        mocked_input.side_effect = ["3", "apple", "sugar", "milk"]
        result = recipe_maker.input_ingredients()
        self.assertEqual(result, "apple,sugar,milk")
        print("Passed")

    # @patch('recipe_maker.requests.get')
    # def test_fetch_recipes(self, mocked_get):
    #     mocked_get.return_value.json.return_value = [{
    #         'title': 'Apple Pie',
    #         'image': 'url_to_image',
    #         'usedIngredients': [{'name': 'apple', 'amount': 3, 'unit':
    #           'units'}],
    #         'missedIngredients': [{'name': 'sugar', 'amount': 100, 'unit':
    #            'grams'}],
    #         'missedIngredientCount': 1
    #     }]
    #     recipes = recipe_maker.fetch_recipes()
    #     self.assertIn('Apple Pie', recipes[0])
    #     self.assertIn('apple: 3 units', recipes[0])
    #     self.assertIn('sugar: 100 grams', recipes[0])


if __name__ == '__main__':
    unittest.main()
