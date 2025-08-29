"""
Real Estate AI Bot - Aplicación Principal
"""

from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
from datetime import datetime

# Imports locales
# Por estas líneas:
try:
    from config.settings import Config
    from core.data_loader import DataLoader
    from core.ai_processor import AIQueryProcessor
    from services.fund_analyzer import FundAnalyzer
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config.settings import Config
    from core.data_loader import DataLoader
    from core.ai_processor import AIQueryProcessor
    from services.fund_analyzer import FundAnalyzer

app = Flask(__name__)
app.config.from_object(Config)

# Variables globales
data_loader = None
ai_processor = None
fund_analyzer = None

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/load-data', methods=['POST'])
def load_data():
    """Cargar datos CSV"""
    global data_loader, ai_processor, fund_analyzer
    
    try:
        data_loader = DataLoader()
        df = data_loader.load_source_fund()
        
        ai_processor = AIQueryProcessor(data_loader)
        fund_analyzer = FundAnalyzer(df)
        
        return jsonify({
            'success': True,
            'message': f'Datos cargados: {len(df):,} registros',
            'stats': {
                'records': len(df),
                'funds': int(df['Fund'].nunique()),
                'metrics': int(df['Data set'].nunique())
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/query', methods=['POST'])
def process_query():
    """Procesar pregunta IA"""
    global ai_processor
    
    try:
        if not ai_processor:
            return jsonify({'success': False, 'error': 'Cargar datos primero'}), 400
        
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'success': False, 'error': 'Pregunta requerida'}), 400
        
        result = ai_processor.process_question(question)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/funds-summary', methods=['GET'])
def get_funds_summary():
    """Resumen de fondos"""
    global fund_analyzer
    
    try:
        if not fund_analyzer:
            return jsonify({'success': False, 'error': 'Cargar datos primero'}), 400
        
        summary = {}
        for fund in fund_analyzer.funds:
            fund_data = fund_analyzer.get_fund_summary(fund)
            if 'error' not in fund_data:
                summary[fund] = {
                    'net_irr': fund_data['metrics'].get('Net IRR', {}).get('value'),
                    'net_tvpi': fund_data['metrics'].get('Net TVPI', {}).get('value'),
                    'nav': fund_data['metrics'].get('NAV', {}).get('value')
                }
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 
