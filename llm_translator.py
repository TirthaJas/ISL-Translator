from groq import Groq
import streamlit as st
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

class LLMTranslator:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.1-8b-instant"

    def translate_with_groq(self, raw_sentence, emotion):
        prompt = f"""You are an Indian Sign Language (ISL) to English translator.

The user signed these words in ISL: "{raw_sentence}"
Their detected emotion is: "{emotion}"

Important notes:
- ISL grammar is different from English grammar
- Facial expressions in ISL can change the meaning of signs
- Convert the ISL signs into natural, fluent English
- Consider the emotion when forming the sentence
- Keep the translation simple and clear
- Return ONLY the translated English sentence, nothing else
- Do NOT include any preamble, explanation, or introduction
- Do NOT start with phrases like "Based on..." or "Here is..."
- Just output the final sentence directly

Translate now:"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=200
        )

        return response.choices[0].message.content.strip().strip('"').strip("'")

    def translate(self, raw_sentence, emotion):
        if not raw_sentence or raw_sentence.strip() == "":
            return "", ""

        result = self.translate_with_groq(
            raw_sentence,
            emotion
        )

        return result, result