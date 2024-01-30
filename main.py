import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QLabel, QVBoxLayout, QLineEdit, QMessageBox
from PyPDF2 import PdfReader

class ATSInterface(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_folder_label = QLabel('Carpeta Seleccionada: Ninguna', self)
        self.init_ui()

    def init_ui(self):
        """
        Inicializa la interfaz de usuario con los elementos necesarios.
        """
        self.select_folder_button = QPushButton('Seleccionar Carpeta', self)
        self.select_folder_button.clicked.connect(self.show_folder_dialog)

        self.indispensable_tech_label = QLabel('Tecnologías Imprescindibles:', self)
        self.indispensable_tech_edit = QLineEdit(self)

        self.desirable_tech_label = QLabel('Tecnologías Deseables:', self)
        self.desirable_tech_edit = QLineEdit(self)

        self.filter_candidates_button = QPushButton('Filtrar Candidatos', self)
        self.filter_candidates_button.clicked.connect(self.filter_candidates)

        layout = QVBoxLayout()
        layout.addWidget(self.selected_folder_label)
        layout.addWidget(self.select_folder_button)
        layout.addWidget(self.indispensable_tech_label)
        layout.addWidget(self.indispensable_tech_edit)
        layout.addWidget(self.desirable_tech_label)
        layout.addWidget(self.desirable_tech_edit)
        layout.addWidget(self.filter_candidates_button)

        self.setLayout(layout)

        self.setGeometry(300, 300, 400, 250)
        self.setWindowTitle('ATS Software')
        self.show()

    def show_folder_dialog(self):
        """
        Muestra un cuadro de diálogo para seleccionar la carpeta.
        """
        try:
            folder_path = QFileDialog.getExistingDirectory(self, 'Seleccionar Carpeta', './')
            if folder_path:
                self.selected_folder_label.setText(f'Carpeta Seleccionada: {folder_path}')
        except Exception as e:
            self.show_error_dialog(f'Error al seleccionar la carpeta: {str(e)}')

    def create_candidate_folders(self, folder_path):
        """
        Crea carpetas necesarias para organizar los candidatos.
        """
        try:
            min_candidate_folder = os.path.join(folder_path, 'Candidato Mínimo')
            plus_candidate_folder = os.path.join(folder_path, 'Candidato Plus')
            unicorn_candidate_folder = os.path.join(folder_path, 'Candidato Unicornio')
            discarded_folder = os.path.join(folder_path, 'Descartados')

            for folder in [min_candidate_folder, plus_candidate_folder, unicorn_candidate_folder, discarded_folder]:
                if not os.path.exists(folder):
                    os.makedirs(folder)

            return min_candidate_folder, plus_candidate_folder, unicorn_candidate_folder, discarded_folder
        except Exception as e:
            self.show_error_dialog(f'Error al crear carpetas: {str(e)}')
            return None, None, None, None

    def filter_candidates(self):
        """
        Filtra los candidatos en base a las tecnologías ingresadas.
        """
        try:
            folder_path = self.selected_folder_label.text().replace('Carpeta Seleccionada: ', '')

            # Verificar que se haya seleccionado una carpeta
            if not folder_path or folder_path == 'Ninguna':
                self.show_error_dialog('Por favor, seleccione una carpeta antes de filtrar candidatos.')
                return

            min_candidate_folder, plus_candidate_folder, unicorn_candidate_folder, discarded_folder = self.create_candidate_folders(folder_path)

            # Verificar que se hayan ingresado tecnologías mínimas
            if not self.indispensable_tech_edit.text().strip():
                self.show_error_dialog('Por favor, ingrese al menos una tecnología imprescindible antes de filtrar candidatos.')
                return

            if min_candidate_folder is None or plus_candidate_folder is None or unicorn_candidate_folder is None or discarded_folder is None:
                return

            indispensable_tech = set(self.indispensable_tech_edit.text().lower().split(','))
            desirable_tech = set(self.desirable_tech_edit.text().lower().split(','))

            for filename in os.listdir(folder_path):
                if filename.endswith('.pdf'):
                    pdf_path = os.path.join(folder_path, filename)
                    category_folder = discarded_folder

                    try:
                        with open(pdf_path, 'rb') as pdf_file:
                            pdf_reader = PdfReader(pdf_file)
                            text = ''.join(page.extract_text() for page in pdf_reader.pages).lower()

                            if all(keyword in text for keyword in indispensable_tech):
                                category_folder = min_candidate_folder

                                if any(keyword in text for keyword in desirable_tech):
                                    category_folder = plus_candidate_folder

                                    if category_folder == plus_candidate_folder:
                                        category_folder = unicorn_candidate_folder
                    except Exception as e:
                        self.show_error_dialog(f'Error al procesar el PDF {filename}: {str(e)}')

                    try:
                        shutil.move(pdf_path, os.path.join(category_folder, filename))
                    except Exception as e:
                        self.show_error_dialog(f'Error al mover el PDF {filename}: {str(e)}')

            QMessageBox.information(self, 'Proceso Completado', 'Proceso de filtrado completado.')
        except Exception as e:
            self.show_error_dialog(f'Error al filtrar candidatos: {str(e)}')

    def show_error_dialog(self, message):
        """
        Muestra un cuadro de diálogo de error.
        """
        QMessageBox.critical(self, 'Error', message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    interface = ATSInterface()
    sys.exit(app.exec_())
