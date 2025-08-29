
### **ARCHIVO 13: tests/test_system.py**

#```python
"""
Tests básicos del sistema
"""
import unittest
import sys
import os

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config
from core.data_loader import DataLoader
from core.ai_processor import AIQueryProcessor
from services.fund_analyzer import FundAnalyzer

class TestRealEstateAI(unittest.TestCase):
    """Tests principales del sistema"""
    
    def setUp(self):
        """Setup para cada test"""
        self.config = Config()
        self.data_loader = DataLoader()
    
    def test_config_loaded(self):
        """Test: Configuración cargada correctamente"""
        self.assertIsNotNone(self.config.DATA_DIR)
        self.assertIsNotNone(self.config.CSV_FILES)
        self.assertIn('source_fund', self.config.CSV_FILES)
    
    def test_data_loader_init(self):
        """Test: DataLoader se inicializa"""
        self.assertIsNotNone(self.data_loader)
        self.assertEqual(len(self.data_loader.data_cache), 0)
    
    def test_file_paths(self):
        """Test: Rutas de archivos son correctas"""
        source_fund_path = os.path.join(
            self.config.DATA_DIR, 
            self.config.CSV_FILES['source_fund']
        )
        
        # El path debe estar bien formado
        self.assertTrue(source_fund_path.endswith('Source Fund.csv'))
    
    def test_ai_processor_init(self):
        """Test: AI Processor se inicializa con DataLoader"""
        ai_processor = AIQueryProcessor(self.data_loader)
        self.assertIsNotNone(ai_processor)
        self.assertEqual(ai_processor.data_loader, self.data_loader)
    
    def test_ai_intent_detection(self):
        """Test: Detección de intenciones funciona"""
        ai_processor = AIQueryProcessor(self.data_loader)
        
        # Test diferentes intenciones
        irr_intent = ai_processor._detect_intent("cuál es el irr del fund i")
        self.assertEqual(irr_intent, 'irr_analysis')
        
        performance_intent = ai_processor._detect_intent("cuál es el mejor fund")
        self.assertEqual(performance_intent, 'performance_ranking')
        
        general_intent = ai_processor._detect_intent("hola como estas")
        self.assertEqual(general_intent, 'general_analysis')
    
    def test_entity_extraction(self):
        """Test: Extracción de entidades"""
        ai_processor = AIQueryProcessor(self.data_loader)
        
        entities = ai_processor._extract_entities("cuál es el irr del fund iii")
        
        self.assertIn('funds', entities)
        self.assertIn('metrics', entities)
        self.assertIn('Fund III', entities['funds'])
        self.assertIn('Net IRR', entities['metrics'])
    
    def test_system_integration(self):
        """Test: Integración básica del sistema"""
        try:
            # Intentar proceso completo (sin datos reales)
            ai_processor = AIQueryProcessor(self.data_loader)
            result = ai_processor.process_question("¿Cuál es el IRR del Fund I?")
            
            # Debe devolver estructura correcta
            self.assertIn('original_question', result)
            self.assertIn('intent', result)
            self.assertIn('entities', result)
            self.assertIn('query_result', result)
            
            # Sin datos, debe dar error específico
            self.assertIn('error', result['query_result'])
            
        except Exception as e:
            self.fail(f"System integration test failed: {str(e)}")

def run_tests():
    """Ejecutar todos los tests"""
    print("🧪 Ejecutando tests del sistema...")
    print("=" * 40)
    
    # Crear test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRealEstateAI)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Reporte final
    print("\n" + "=" * 40)
    if result.wasSuccessful():
        print("✅ Todos los tests pasaron exitosamente!")
        print(f"✅ Tests ejecutados: {result.testsRun}")
    else:
        print("❌ Algunos tests fallaron:")
        print(f"💥 Errores: {len(result.errors)}")
        print(f"💥 Fallas: {len(result.failures)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # Ejecutar tests si se llama directamente
    success = run_tests()
    exit(0 if success else 1) 
