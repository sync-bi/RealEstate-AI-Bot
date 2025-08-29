"""
Módulo de carga de datos CSV
"""
import pandas as pd
import os
from datetime import datetime
from config.settings import Config

class DataLoader:
    """Carga y valida archivos CSV"""
    
    def __init__(self):
        self.data_cache = {}
        self.config = Config()
    
    def load_source_fund(self):
        """Carga Source Fund.csv"""
        try:
            file_path = os.path.join(
                self.config.DATA_DIR, 
                self.config.CSV_FILES['source_fund']
            )
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
            # Leer con delimitador pipe
            df = pd.read_csv(file_path, delimiter='|', encoding='utf-8')
            
            # Limpiar datos
            df.columns = df.columns.str.strip()
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Data'] = pd.to_numeric(df['Data'], errors='coerce')
            
            # Filtrar datos válidos
            df = df.dropna(subset=['Data'])
            df = df[df['Fund'] != '']
            
            # Guardar en cache
            self.data_cache['source_fund'] = df
            
            print(f"✅ Cargados {len(df)} registros")
            return df
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise e
    
    def get_cached_data(self, table_name):
        """Obtiene datos del cache"""
        return self.data_cache.get(table_name)
    
    def is_data_loaded(self, table_name):
        """Verifica si hay datos cargados"""
        return table_name in self.data_cache 
