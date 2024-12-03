from better_profanity import profanity
import re

class ContentModerator:
    def __init__(self):
        profanity.load_censor_words()
        # Adiciona palavras em português
        palavras_proibidas = [
            'palavrão1', 'palavrão2',  # Adicione palavrões em português aqui
            'calúnia', 'difamação',
            'assédio', 'discriminação',
            'merda', 'porra', 'caralho', 'puta',
            'viado', 'bicha', 'sapatão',
            'preto', 'macaco',  # termos racistas
            'retardado', 'mongol',  # capacitismo
            'judeu', 'turco',  # xenofobia
        ]
        profanity.add_censor_words(palavras_proibidas)
    
    def check_content(self, text):
        """
        Retorna um dicionário com os resultados da moderação
        """
        results = {
            'contains_profanity': False,
            'contains_personal_info': False,
            'should_block': False,
            'reason': []
        }
        
        # Verifica palavrões
        if profanity.contains_profanity(text):
            results['contains_profanity'] = True
            results['reason'].append('Conteúdo impróprio detectado')
            results['should_block'] = True
        
        # Verifica informações pessoais (emails, telefones, etc)
        if self._contains_personal_info(text):
            results['contains_personal_info'] = True
            results['should_block'] = True
            results['reason'].append('Informações pessoais detectadas')
        
        return results
    
    def _contains_personal_info(self, text):
        """
        Verifica se o texto contém informações pessoais
        """
        # Padrão para email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        # Padrão para telefone brasileiro
        phone_pattern = r'(\(?\d{2}\)?\s)?(\d{4,5}\-\d{4})'
        # Padrão para CPF
        cpf_pattern = r'\d{3}\.?\d{3}\.?\d{3}\-?\d{2}'
        # Padrão para links
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        
        patterns = [email_pattern, phone_pattern, cpf_pattern, url_pattern]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def censor_text(self, text):
        """
        Censura palavras impróprias no texto
        """
        return profanity.censor(text)

# Singleton para uso em toda a aplicação
moderator = ContentModerator()
