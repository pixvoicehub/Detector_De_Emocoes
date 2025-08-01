# Importações necessárias para um web service (ex: Flask, FastAPI)
# Estou usando Flask como exemplo, pois é muito comum. Adapte se estiver usando outro.
from flask import Flask, request, jsonify
import os
import genai # Supondo que a biblioteca do Google se chame 'genai'

# --- Configuração Inicial ---

# Inicializa o aplicativo Flask
app = Flask(__name__)

# Carrega a chave da API do Gemini a partir das variáveis de ambiente do Render.com
# É uma prática de segurança importante não deixar a chave no código.
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    # Se a chave não for encontrada, o serviço não pode funcionar.
    # Isso será logado no Render para que você saiba do problema.
    raise ValueError("A variável de ambiente GEMINI_API_KEY não foi definida.")

# Configura a API do Google AI
genai.configure(api_key=gemini_api_key)

# --- Funções Auxiliares ---

def get_all_tags_string():
    """
    Esta função deve retornar a string completa de todas as tags disponíveis.
    Idealmente, ela leria o arquivo JSON de emoções que você tem.
    Por simplicidade aqui, vamos simular o resultado.
    """
    # Em um cenário real, você leria e processaria seu arquivo JSON aqui.
    # Ex: with open('emotions.json', 'r') as f: data = json.load(f) ...
    # Por enquanto, uma string de exemplo para o prompt funcionar.
    return "<joy>, <sadness>, <emphasis_strong>, <pause_medium>, <smiling_tone>, etc."

# --- Rota Principal da API ---

# Define o endpoint que o seu PHP está chamando: /api/humanize-text
@app.route('/api/humanize-text', methods=['POST'])
def humanize_text_endpoint():
    try:
        # 1. Recebe os dados JSON enviados pelo PHP
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Nenhum dado JSON recebido.'}), 400

        # 2. Extrai todas as variáveis do JSON, com valores padrão para segurança
        text_to_analyze = data.get('text', '')
        if not text_to_analyze:
            return jsonify({'success': False, 'error': 'O campo "text" é obrigatório.'}), 400

        humanization_level = data.get('humanization_level', 3)
        add_pauses = data.get('add_pauses', False)
        add_emphasis = data.get('add_emphasis', False)
        add_hesitations = data.get('add_hesitations', False)
        add_conversational = data.get('add_conversational', False)
        add_breathing = data.get('add_breathing', False)
        
        # [CORREÇÃO] Recebe a nova variável 'add_smiling_tone' do JSON.
        # Se ela não for enviada, o padrão é 'False'.
        add_smiling_tone = data.get('add_smiling_tone', False)

        # 3. Engenharia de Prompt Avançada
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
        
        if add_breathing:
            instructions.append("Insira a tag <breath> no início de frases ou antes de cláusulas importantes para simular uma inspiração natural do locutor.")
            
        # [CORREÇÃO] Adiciona a instrução para o tom sorridente se o checkbox estiver marcado.
        if add_smiling_tone:
            instructions.append("Adote um 'tom sorridente' (smiling voice) como base para a narração. Isso significa que, mesmo em momentos neutros, a voz deve soar amigável, calorosa e otimista. Use isso para modular outras emoções. Por exemplo, uma <surpresa> deve ser agradável, e uma <ênfase> deve ser positiva.")
            
        instructions.append("IMPORTANTE: Sua resposta deve conter APENAS o texto modificado com as tags inseridas. Não inclua nenhuma explicação, prefácio ou qualquer texto adicional.")
        
        final_prompt = "\n".join(instructions) + f"\n\nTexto original para reescrever:\n---\n{text_to_analyze}"
        
        # 4. Geração do conteúdo pela IA
        response = model.generate_content(final_prompt)
        
        # 5. Retorno da resposta de sucesso
        # Acessa o texto gerado. A forma de acessar pode variar um pouco (ex: response.text ou response.parts[0].text)
        humanized_text = response.text
        
        return jsonify({
            'success': True,
            'humanized_text': humanized_text
        }), 200

    except Exception as e:
        # Captura qualquer erro inesperado durante o processo e o loga no Render
        print(f"Erro inesperado no servidor de análise: {e}")
        return jsonify({'success': False, 'error': f'Erro interno no servidor de análise: {str(e)}'}), 500

# --- Execução do Servidor ---

# Esta parte permite que o serviço rode no Render.com
if __name__ == "__main__":
    # O Render define a porta através da variável de ambiente PORT
    port = int(os.environ.get("PORT", 8080))
    # '0.0.0.0' é necessário para que o serviço seja acessível externamente
    app.run(host='0.0.0.0', port=port)
