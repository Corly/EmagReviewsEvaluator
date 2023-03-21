from deep_translator import GoogleTranslator

class LeTranslator:
    def __init__(self):
        self.translator_ro_en = GoogleTranslator(source='ro', target='en')
        self.translator_en_ro = GoogleTranslator(source='en', target='ro')

    def translate_ro_en(self, text):
        return self.translator_ro_en.translate(text)
    
    def translate_en_ro(self, text):
        return self.translator_en_ro.translate(text)
    

if __name__ == "__main__":
    translator = LeTranslator()
    text = "Salut, cum te cheama?"
    en_translation = translator.translate_ro_en(text)
    ro_translation = translator.translate_en_ro(en_translation)
    print(f"Original: {text}")
    print(f"English: {en_translation}")
    print(f"Romanian: {ro_translation}")