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
            - Workflow:
            1. Receive original English poem text.
            2. Analyze the structure and meaning of the poem.
            3. Identify abstract concepts, metaphors, and poetic devices (e.g., repetition, sound, imagery).
            4. Use ASL gloss grammar tools for automated translation, also need to follow these grammar:
            Never use linking verbs (am, is, are, was, were).
            Never use endings (s, ed, ing, er, est ).
            Nouns are singular, verbs are present tense.
            Remove the hyphens between words.
            Use ME for I always.
            Sentences are in time, topic, comment order. a. Time words come first (today, tomorrow, later, yesterday, now) b. Topic (subject in noun phrase or objects in verb phrase) depends what is more important c. Comment (verb phrase including action)
            Capitalize all signs.
            Fingerspelled names are written fs-Wilson.
            Uncommon items or concepts that are rarely included in the lexicon can also be fingerspelled as fs-XXX
            Adjectives are usually after nouns.
            Adverbs are expressed with the way a sign is signed and NMS.
            Don’t use punctuation.
            The WH words come at the end of the sentence.
            When in doubt DON’T use initialized signs.
            Words that are irrelevant in the sentence leave out. (the, although, of, ....)
            You don’t sign WH words unless it is a question.
            Do remember: no -ed, -ing! Never use endings (s, ed, ing, er, est ).
            Focus on conveying the core meaning and concepts, not a word-for-word translation. Use ASL-specific grammar and structure, and adjust for natural hand-sign expressions. Omit unnecessary auxiliary verbs, articles, and prepositions. If the sentence involves a complex structure, focus on the primary action and its core components. Do not translate the sentence literally; instead, focus on the key message and how it would be conveyed in ASL, taking cultural context into account.
            4. Perform context analysis to ensure accuracy of professional terms and complex ASL gloss expressions.
            5. Manual review to ensure text fluency and accuracy. 
            - Examples:
            - Original text: *In darkening air, a street band still launches bright trumpet trills...*
            - Corrected ASL gloss: *DARK AIR STREET BAND STILL SOUND TRUMPET BRIGHT*

            - Original text: *But there’s a loophole in the water that God could walk through...*
            - Corrected ASL gloss: *WATER LOOPHOLE GOD WALK THROUGH* 
            
            - Original text: *This is how the blame game starts...*
            - Corrected ASL gloss: *BLAME GAME HOW START*  
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
