from googletrans import Translator
translator = Translator(service_urls=["translate.googleapis.com"])


def translate_listing(text, target_lang):
    # use translate method to translate a string - by default, the destination language is english
    translated = translator.translate(text, dest=target_lang)

    # the translate method returns an object
    # Translated(src=es, dest=en, text=Hello World, pronunciation=Hello World, extra_data="{'translat...")

    # obtain translated string by using attribute .text
    return translated.text
    # 'Hello World'
