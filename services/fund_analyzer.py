"""
Servicio de análisis de fondos
"""
import pandas as pd

class FundAnalyzer:
    """Análisis especializado de fondos"""
    
    def __init__(self, data):
        self.data = data
        self.funds = self._get_active_funds()
    
    def _get_active_funds(self):
        """Obtiene fondos activos"""
        return [fund for fund in self.data['Fund'].unique() if fund != 'Total']
    
    def get_fund_summary(self, fund_name):
        """Resumen completo de un fondo"""
        if fund_name not in self.funds:
            return {'error': f'Fondo {fund_name} no encontrado'}
        
        fund_data = self.data[self.data['Fund'] == fund_name]
        
        summary = {
            'fund_name': fund_name,
            'total_records': len(fund_data),
            'metrics': {}
        }
        
        # Métricas principales
        key_metrics = ['Net IRR', 'Net TVPI', 'NAV', 'Net DPI']
        
        for metric in key_metrics:
            metric_data = fund_data[fund_data['Data set'] == metric]
            if len(metric_data) > 0:
                latest_value = metric_data.iloc[-1]['Data']
                summary['metrics'][metric] = {
                    'value': latest_value,
                    'formatted': self._format_value(metric, latest_value)
                }
        
        return summary
    
    def compare_funds(self, fund_list):
        """Compara múltiples fondos"""
        comparison = {}
        
        for fund in fund_list:
            if fund in self.funds:
                comparison[fund] = self.get_fund_summary(fund)
        
        return {
            'comparison_type': 'Multi-fund comparison',
            'funds_compared': fund_list,
            'data': comparison
        }
    
    def _format_value(self, metric, value):
        """Formatea valores según métrica"""
        if value is None:
            return 'N/A'
        
        if 'IRR' in metric:
            return f"{value * 100:.2f}%"
        elif 'TVPI' in metric or 'DPI' in metric:
            return f"{value:.2f}x"
        else:
            return f"{value:,.2f}" 
