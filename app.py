# Importa a biblioteca oficial do Google
import google.generativeai as genai

# Esta função é o núcleo do seu script.
# Ela recebe os dados e retorna o texto processado.
def process_text_with_emotions(data):
    """
    Processa o texto para adicionar tags de emoção com base nos parâmetros fornecidos.
    """
    try:
        # 1. Extrai todas as variáveis do dicionário 'data'
        text_to_analyze = data.get('text', '')
        humanization_level = data.get('humanization_level', 3)
        add_pauses = data.get('add_pauses', False)
        add_emphasis = data.get('add_emphasis', False)
        add_hesitations = data.get('add_hesitations', False)
        add_conversational = data.get('add_conversational', False)
        add_breathing = data.get('add_breathing', False)
        
        # [CORREÇÃO] Recebe a nova variável 'add_smiling_tone'.
        # Este é o ponto crucial que estava faltando.
        add_smiling_tone = data.get('add_smiling_tone', False)

        # 2. Configura a API do Gemini (supondo que a chave já foi configurada antes)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # Você teria uma função para carregar suas tags aqui
        available_tags = "<joy>, <sadness>, <emphasis_strong>, <pause_medium>, <smiling_tone>, etc."
        
        # 3. Constrói a lista de instruções para o prompt
        instructions = [
            f"Sua tarefa é atuar como um diretor de voz profissional para um sistema de Text-to-Speech. Você deve reescrever o texto fornecido, inserindo tags de emoção e estilo para torná-lo mais humano e expressivo. As tags disponíveis são: {available_tags}.",
            "Analise o texto frase por frase e insira as tags apropriadas onde a emoção ou o tom mudam.",
            f"O Nível de Humanização solicitado é {humanization_level} (em uma escala de 0 a 5). 0 é quase nenhuma alteração, 3 é um nível natural e 5 é extremamente expressivo e dramático. Ajuste a frequência e a intensidade das tags de acordo com este nível."
        ]
        
        if add_pauses:
            instructions.append("Insira pausas (<pause_short>, <pause_medium>, etc.) de forma natural para melhorar o ritmo da fala.")
        if add_emphasis:
            instructions.append("Use tags de ênfase (<emphasis_soft>, <emphasis_strong>) para destacar palavras ou frases importantes.")
        if add_hesitations:
            instructions.append("Se o nível de humanização for 3 ou maior, adicione pequenas hesitações (como 'uhm...', 'ahh...') onde faria sentido em uma conversa natural.")
        if add_conversational:
            instructions.append("Incorpore elementos conversacionais, como pequenas interjeições ou marcadores discursivos ('sabe?', 'né?'), se apropriado para o contexto e nível de humanização.")
        if add_breathing:
            instructions.append("Insira a tag <breath> no início de frases ou antes de cláusulas importantes para simular uma inspiração natural do locutor.")
            
        # [CORREÇÃO] Adiciona a instrução do sorriso se a variável for verdadeira.
        if add_smiling_tone:
            instructions.append("Adote um 'tom sorridente' (smiling voice) como base para a narração. Isso significa que, mesmo em momentos neutros, a voz deve soar amigável, calorosa e otimista. Use isso para modular outras emoções. Por exemplo, uma <surpresa> deve ser agradável, e uma <ênfase> deve ser positiva.")
            
        instructions.append("IMPORTANTE: Sua resposta deve conter APENAS o texto modificado com as tags inseridas. Não inclua nenhuma explicação, prefácio ou qualquer texto adicional.")
        
        # 4. Monta o prompt final e gera o conteúdo
        final_prompt = "\n".join(instructions) + f"\n\nTexto original para reescrever:\n---\n{text_to_analyze}"
        
        response = model.generate_content(final_prompt)
        
        # 5. Retorna o texto gerado com sucesso
        return response.text

    except Exception as e:
        # Se qualquer erro ocorrer, ele será "levantado" para que o script que chamou esta função possa tratá-lo.
        # Isso é importante para o debug.
        print(f"Erro durante o processamento do texto: {e}")
        raise e

# Exemplo de como este script seria usado por um framework como Flask:
#
# from flask import Flask, request, jsonify
# import os
#
# app = Flask(__name__)
# genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
#
# @app.route('/api/humanize-text', methods=['POST'])
# def api_endpoint():
#     try:
#         data = request.get_json()
#         humanized_text = process_text_with_emotions(data)
#         return jsonify({'success': True, 'humanized_text': humanized_text}), 200
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500
