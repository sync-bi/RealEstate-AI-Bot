"""
Motor de IA para procesar preguntas
"""
import re
import pandas as pd
from core.data_loader import DataLoader

class AIQueryProcessor:
    """Procesa preguntas en lenguaje natural"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
    
    def process_question(self, question):
        """Procesa una pregunta"""
        question_lower = question.lower()
        
        # Detectar intención
        intent = self._detect_intent(question_lower)
        
        # Extraer entidades
        entities = self._extract_entities(question_lower)
        
        # Ejecutar consulta
        query_result = self._execute_query(intent, entities)
        
        return {
            'original_question': question,
            'intent': intent,
            'entities': entities,
            'query_result': query_result,
            'confidence': 0.85
        }
    
    def _detect_intent(self, question):
        """Detecta intención de la pregunta"""
        if 'irr' in question:
            return 'irr_analysis'
        elif 'mejor' in question or 'best' in question:
            return 'performance_ranking'
        elif 'distribu' in question:
            return 'distribution_analysis'
        elif 'comparar' in question:
            return 'comparison'
        else:
            return 'general_analysis'
    
    def _extract_entities(self, question):
        """Extrae fondos y métricas"""
        entities = {'funds': [], 'metrics': []}
        
        # Detectar fondos
        fund_matches = re.findall(r'fund\s+([iv]+)', question)
        entities['funds'] = [f"Fund {f.upper()}" for f in fund_matches]
        
        # Detectar métricas
        if 'irr' in question:
            entities['metrics'].append('Net IRR')
        elif 'nav' in question:
            entities['metrics'].append('NAV')
        elif 'tvpi' in question:
            entities['metrics'].append('Net TVPI')
        
        return entities
    
    def _execute_query(self, intent, entities):
        """Ejecuta consulta según intención"""
        if not self.data_loader.is_data_loaded('source_fund'):
            return {'error': 'Datos no cargados'}
        
        df = self.data_loader.get_cached_data('source_fund')
        
        try:
            if intent == 'irr_analysis':
                return self._analyze_irr(df, entities)
            elif intent == 'performance_ranking':
                return self._rank_performance(df)
            elif intent == 'distribution_analysis':
                return self._analyze_distributions(df)
            else:
                return self._general_summary(df)
        except Exception as e:
            return {'error': f'Error: {str(e)}'}
    
    def _analyze_irr(self, df, entities):
        """Análisis de IRR"""
        irr_data = df[df['Data set'] == 'Net IRR']
        results = {}
        
        funds = entities['funds'] if entities['funds'] else [f for f in df['Fund'].unique() if f != 'Total']
        
        for fund in funds:
            fund_data = irr_data[irr_data['Fund'] == fund]
            if len(fund_data) > 0:
                latest_irr = fund_data.iloc[-1]['Data']
                results[fund] = {
                    'net_irr': latest_irr,
                    'percentage': f"{latest_irr * 100:.2f}%" if latest_irr else 'N/A'
                }
        
        return {
            'analysis_type': 'Análisis de IRR',
            'results': results,
            'summary': f"IRR de {len(results)} fondos"
        }
    
    def _rank_performance(self, df):
        """Ranking por performance"""
        net_irr = df[df['Data set'] == 'Net IRR'].groupby('Fund')['Data'].last()
        net_irr = net_irr[net_irr.index != 'Total'].sort_values(ascending=False)
        
        return {
            'analysis_type': 'Ranking de Performance',
            'results': net_irr.to_dict(),
            'best_performer': net_irr.index[0] if len(net_irr) > 0 else None,
            'summary': f"Ranking de {len(net_irr)} fondos"
        }
    
    def _analyze_distributions(self, df):
        """Análisis de distribuciones"""
        dist_data = df[df['Data set'].str.contains('Distribution|DPI', na=False)]
        results = {}
        
        for fund in df['Fund'].unique():
            if fund != 'Total':
                fund_data = dist_data[dist_data['Fund'] == fund]
                if len(fund_data) > 0:
                    results[fund] = {'distributions': len(fund_data)}
        
        return {
            'analysis_type': 'Análisis de Distribuciones',
            'results': results,
            'summary': f"Distribuciones de {len(results)} fondos"
        }
    
    def _general_summary(self, df):
        """Resumen general"""
        return {
            'analysis_type': 'Resumen General',
            'results': {
                'total_records': len(df),
                'unique_funds': df['Fund'].nunique(),
                'available_metrics': df['Data set'].nunique()
            },
            'summary': 'Estadísticas del dataset'
        } 
