import sys
from PyQt5.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.core.voice_processor import VoiceProcessor
from app.core.mistral_integration import MistralModel
from app.core.knowledge_base.knowledge_manager import KnowledgeManager

class MedicalAssistantApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.voice_processor = VoiceProcessor()
        self.knowledge_manager = KnowledgeManager()
        self.mistral = MistralModel()
        
        # Initialize main window
        self.main_window = MainWindow(
            voice_processor=self.voice_processor,
            knowledge_manager=self.knowledge_manager,
            mistral_model=self.mistral
        )

    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    app = MedicalAssistantApp()
    app.run()