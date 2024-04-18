class NLP:
    def __init__(self):
        news_summary = pd.read_csv("news_summary.csv", encoding="latin-1")
        texto_noticias = self.news_summary["text"].to_list()
        subset_noticias = self.texto_noticias[0:100]
        
    # Adaptar a tokenizacion colectiva
    def visualizador_de_tokens(data, unity, restriction=False,
                               number_restriction=5):
        # Contador
        i = 0
        example_data = data[unity]
        token = word_tokenize(example_data)
        
        # Restriction
        for num, token in enumerate(token):
            i += 1
            if restriction == True:
                if i < number_restriction + 1:
                    print(f"Token num {num} is {token}")
                else:
                    break
            else:
                print(f"Token num {num} is {token}")
        return
                          
                          
                          
    #  Adaptar a dvision colectiva
    def dividir_oraciones_nlp(datos, documento, fragment = False, frag_num =2):
        lista_documentos = [modelo(documento) for noticia in datos]
        if fragment == True:
            for num, sentence in enumerate(lista_documentos[frag_num].sents):
                print(f"La oracion numero {num}es: \n {sentence}")
        return
        
                          
    def extraer_ngramas(datos, numero):
        n_grams = ngrams(word_tokenize(datos), numero)
        return [ ' '.join(grams) for grams in n_grams] # Utilizar en conjunto con map o apply 