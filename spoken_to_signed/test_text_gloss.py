from openai import OpenAI
from config import *
import cv2


def read_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


client = OpenAI(
    api_key=apikey,
)

def correct_ocr_text(user_input_text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"""
            - Role: ASL gloss translation specialist for poetry
            - Background: Users need to accurately translate English poetry into American Sign Language (ASL) gloss while preserving the essence, imagery, and emotional tone of the poem.
            - Profile: You are a professional ASL gloss translation specialist skilled in translating poetic language, metaphors, abstract concepts, and complex imagery into clear and expressive ASL gloss.
            - Skills: Language comprehension, spelling correction, grammar correction, terminology recognition, context analysis. Understanding abstract language, metaphorical interpretation, visual expression, rhythm and flow in ASL, dynamic translation of poetic devices like repetition and sound.
            - Goals: Design a process that conveys the poem’s imagery, rhythm, and metaphorical meaning in ASL gloss while ensuring fluency and clarity.
            - Constraints: The translation process needs to be accurate and efficient while maintaining the original meaning and format of the text. The translation should stay true to the original meaning and metaphorical essence of the poem. The translation should use ASL gloss grammar but may adapt the structure for clarity, flow, and poetic impact. Maintain visual fluency and expressiveness while respecting ASL grammar. Avoid literal word-for-word translation—focus on visual representation and figurative meaning.
            - OutputFormat: The corrected ASL gloss should maintain the poem’s poetic structure, but follow ASL conventions for clarity and expressiveness. Remember: Only output the translated ASL gloss, do not output other information.
            - 
            - I need to generate ASL based on ASL Gloss, and I need you to help me complete the step of converting the input poem into Gloss. Note that poetry is obscure, difficult to understand, and abstract, so you cannot translate word by word, but should find a suitable translation method for poetry based on the context. Sign conceptually, not every words. I need to find lexicon based on Gloss and finally generate ASL, so the Gloss you generate is very important to me. Please understand the poem as much as possible and translate it into appropriate Gloss, and these Gloss are also easy to generate subsequent ASL.
            original text: {user_input_text}
            """},
            {"role": "user", "content": user_input_text}
        ]
    )

    corrected_input = response.choices[0].message.content
    return corrected_input


if __name__ == "__main__":
    user_input = "../input_poems/New_Orleans_Function_by_Michael_Collins.txt"
    user_input_text = read_text_from_file(user_input)
    result = correct_ocr_text(user_input_text)
    print(result)

# user_input = "this report takes no cognisance of hazard or risk it cannot identify between the two of them ."

# user_input = "I have a tiger."
#
# corrected_text = correct_ocr_text(user_input)
# print(corrected_text)
