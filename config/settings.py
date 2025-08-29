"""
Configuración del sistema
"""
import os

class Config:
    """Configuración base"""
    
    # Directorios
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # Archivos CSV
    CSV_FILES = {
        'source_fund': 'Source Fund.csv',
        'wf_assumptions': 'WF assumptions.csv',
        'date_table': 'Date.csv',
        'test_append': 'Test.csv'
    }
    
    # Flask
    SECRET_KEY = 'dev-secret-key-change-in-production'
    DEBUG = True 
