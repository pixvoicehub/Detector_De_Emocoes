import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# Inicialização da aplicação Flask
app = Flask(__name__)
CORS(app) # Habilita CORS para todas as rotas

# Carrega a lista de emoções/tags de um arquivo local.
# Certifique-se de que o arquivo 'emocoes.json' está no mesmo diretório.
try:
    with open('emocoes.json', 'r', encoding='utf-8') as f:
        EMOTION_TAGS_DATA = json.load(f)
except FileNotFoundError:
    EMOTION_TAGS_DATA = {}

def get_all_tags_string():
    """Formata todas as tags disponíveis em uma string para o prompt."""
    all_tags = []
    for category in EMOTION_TAGS_DATA.values():
        for item in category:
            all_tags.append(item['comando'])
    # [NOVO] Adiciona a tag customizada de respiração à lista de tags disponíveis
    all_tags.append('<breath>')
    return ", ".join(sorted(list(set(all_tags)))) # Ordena e remove duplicatas

# Endpoint raiz para verificação de status
@app.route('/')
def home():
    return "Serviço de Injeção de Emoções está online."

@app.route('/health')
def health_check():
    return "API is awake and healthy.", 200

# Endpoint principal para humanizar o texto
@app.route('/api/humanize-text', methods=['POST'])
def humanize_text_endpoint():
    # 1. Validação da Chave da API e dos Dados de Entrada
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        return jsonify({"error": "Configuração do servidor Gemini incompleta."}), 500
    
    data = request.get_json()
    if not data or not data.get('text'):
        return jsonify({"error": "Texto para análise não pode estar vazio."}), 400
    
    # 2. Extração de todos os Parâmetros
    text_to_analyze = data.get('text')
    humanization_level = data.get('humanization_level', 3)
    add_pauses = data.get('add_pauses', False)
    add_emphasis = data.get('add_emphasis', False)
    add_hesitations = data.get('add_hesitations', False)
    add_conversational = data.get('add_conversational', False)
    add_breathing = data.get('add_breathing', False) # [NOVO] Captura o novo parâmetro
    
    # 3. Engenharia de Prompt Avançada
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        available_tags = get_all_tags_string()
        
        # Construção dinâmica do prompt com base nas opções do usuário
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
        
        # [NOVO] Adiciona a instrução para a respiração
        if add_breathing:
            instructions.append("Insira a tag <breath> no início de frases ou antes de cláusulas importantes para simular uma inspiração natural do locutor.")
            
        instructions.append("IMPORTANTE: Sua resposta deve conter APENAS o texto modificado com as tags inseridas. Não inclua nenhuma explicação, prefácio ou qualquer texto adicional.")
        
        final_prompt = "\n".join(instructions) + f"\n\nTexto original para reescrever:\n---\n{text_to_analyze}"
        
        response = model.generate_content(final_prompt)
        
        # 4. Retorna o texto modificado
        humanized_text = response.text.strip()

        return jsonify({
            "success": True,
            "humanized_text": humanized_text
        })

    except Exception as e:
        print(f"Erro na API Gemini (Humanização): {e}")
        return jsonify({"error": f"Erro ao processar o texto: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)