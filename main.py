import subprocess
import sys

# Verification et installation automatique des prerequis
try:
    from PyQt5 import QtCore, QtGui, QtWidgets
except ImportError:
    print("PyQt5 manquant. Installation en cours...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
    from PyQt5 import QtCore, QtGui, QtWidgets

import os
import base64

class UntardleApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Untardle Archiver (.unt)")
        self.resize(600, 400)
        
        layout = QtWidgets.QVBoxLayout()
        
        # Onglets Mode Compression / Mode Decompression
        self.tabs = QtWidgets.QTabWidget()
        self.tab_compress = QtWidgets.QWidget()
        self.tab_decompress = QtWidgets.QWidget()
        
        self.tabs.addTab(self.tab_compress, "Compresser (Créer .unt)")
        self.tabs.addTab(self.tab_decompress, "Décompresser (Extraire .unt)")
        
        self.setup_compress_tab()
        self.setup_decompress_tab()
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
    def setup_compress_tab(self):
        layout = QtWidgets.QVBoxLayout(self.tab_compress)
        
        self.btn_select_dir = QtWidgets.QPushButton("Sélectionner le dossier à compresser")
        self.btn_select_dir.clicked.connect(self.select_source_dir)
        layout.addWidget(self.btn_select_dir)
        
        self.lbl_source = QtWidgets.QLabel("Aucun dossier sélectionné")
        self.lbl_source.setStyleSheet("color: gray;")
        layout.addWidget(self.lbl_source)
        
        layout.addWidget(QtWidgets.QLabel("Nom du fichier de sortie (sans extension) :"))
        self.input_filename = QtWidgets.QLineEdit()
        self.input_filename.setPlaceholderText("mon_archive")
        layout.addWidget(self.input_filename)
        
        self.btn_run_compress = QtWidgets.QPushButton("Créer l'archive .unt")
        self.btn_run_compress.clicked.connect(self.process_compression)
        layout.addWidget(self.btn_run_compress)
        
        self.source_dir = ""
        
    def setup_decompress_tab(self):
        layout = QtWidgets.QVBoxLayout(self.tab_decompress)
        
        self.btn_select_file = QtWidgets.QPushButton("Sélectionner un fichier .unt")
        self.btn_select_file.clicked.connect(self.select_unt_file)
        layout.addWidget(self.btn_select_file)
        
        self.lbl_file = QtWidgets.QLabel("Aucun fichier sélectionné")
        self.lbl_file.setStyleSheet("color: gray;")
        layout.addWidget(self.lbl_file)
        
        self.btn_select_dest = QtWidgets.QPushButton("Sélectionner le dossier de destination")
        self.btn_select_dest.clicked.connect(self.select_dest_dir)
        layout.addWidget(self.btn_select_dest)
        
        self.lbl_dest = QtWidgets.QLabel("Aucun dossier sélectionné")
        self.lbl_dest.setStyleSheet("color: gray;")
        layout.addWidget(self.lbl_dest)
        
        self.btn_run_decompress = QtWidgets.QPushButton("Extraire l'archive")
        self.btn_run_decompress.clicked.connect(self.process_decompression)
        layout.addWidget(self.btn_run_decompress)
        
        self.unt_file = ""
        self.dest_dir = ""

    def select_source_dir(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Choisir le dossier source")
        if directory:
            self.source_dir = directory
            self.lbl_source.setText(directory)
            
    def select_unt_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choisir le fichier .unt", "", "Fichiers Untardle (*.unt)")
        if file_path:
            self.unt_file = file_path
            self.lbl_file.setText(file_path)
            
    def select_dest_dir(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Choisir le dossier d'extraction")
        if directory:
            self.dest_dir = directory
            self.lbl_dest.setText(directory)

    # --- ARCHIVAGE (COMPRESSION) ---
    def process_compression(self):
        if not self.source_dir or not os.path.exists(self.source_dir):
            QtWidgets.QMessageBox.warning(self, "Erreur", "Veuillez selectionner un dossier source valide.")
            return
            
        out_name = self.input_filename.text().strip()
        if not out_name:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Veuillez entrer un nom de fichier valide.")
            return
            
        parent_dir = os.path.dirname(self.source_dir)
        output_path = os.path.join(parent_dir, f"{out_name}.unt")
        
        print("Debut de la compression...")
        
        try:
            with open(output_path, "w", encoding="utf-8") as f_out:
                f_out.write("!/.unt!\\\n")
                
                for root, dirs, files in os.walk(self.source_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        base_parent = os.path.dirname(self.source_dir)
                        rel_path = os.path.relpath(full_path, base_parent)
                        formatted_key = "/" + rel_path.replace("\\", "/")
                        
                        print(f"Archivage de : {formatted_key}")
                        
                        # Lecture en mode binaire 'rb' pour supporter exe, zip, images, etc.
                        try:
                            with open(full_path, "rb") as f_in:
                                binary_data = f_in.read()
                                # Encodage en base64 pour l'ecrire proprement en texte pur ascii
                                b64_data = base64.b64encode(binary_data).decode("utf-8")
                        except Exception as e:
                            print(f"Erreur de lecture pour {file} : {str(e)}")
                            b64_data = ""
                        
                        f_out.write(f"{formatted_key} : </file-start/>\n")
                        f_out.write(b64_data)
                        f_out.write("\n</file-end/>\n")
            
            print("Compression terminee avec succes !")
            QtWidgets.QMessageBox.information(self, "Succès", f"Archive Untardle créée avec succès :\n{output_path}")
            
        except Exception as e:
            print(f"Erreur durant l'ecriture : {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")

    # --- DESARCHIVAGE (DECOMPRESSION) ---
    def process_decompression(self):
        if not self.unt_file or not os.path.exists(self.unt_file):
            QtWidgets.QMessageBox.warning(self, "Erreur", "Veuillez selectionner un fichier .unt valide.")
            return
        if not self.dest_dir or not os.path.exists(self.dest_dir):
            QtWidgets.QMessageBox.warning(self, "Erreur", "Veuillez selectionner un dossier de destination valide.")
            return
            
        print("Debut de la decompression...")
        
        try:
            with open(self.unt_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            if not lines or "!/.unt!\\" not in lines[0]:
                QtWidgets.QMessageBox.critical(self, "Erreur", "Le fichier n'est pas un format .unt valide.")
                return
                
            current_file_path = None
            current_content = []
            inside_file = False
            
            for line in lines[1:]:
                if "</file-start/>" in line and not inside_file:
                    parts = line.split(" : </file-start/>")
                    if parts:
                        raw_path = parts[0].strip()
                        if raw_path.startswith("/"):
                            raw_path = raw_path[1:]
                        current_file_path = os.path.join(self.dest_dir, raw_path)
                        inside_file = True
                        current_content = []
                    continue
                
                if "</file-end/>" in line and inside_file:
                    file_dir = os.path.dirname(current_file_path)
                    if not os.path.exists(file_dir):
                        os.makedirs(file_dir, exist_ok=True)
                        
                    full_b64_text = "".join(current_content).strip()
                    
                    # Decodage du base64 pour retrouver les octets d'origine exacts
                    try:
                        decoded_bytes = base64.b64decode(full_b64_text)
                    except Exception as e:
                        print(f"Erreur decodage base64 : {str(e)}")
                        decoded_bytes = b""
                        
                    print(f"Extraction binaire de : {current_file_path}")
                    # Ecriture en mode binaire 'wb' pour restituer le fichier original intact
                    with open(current_file_path, "wb") as f_out:
                        f_out.write(decoded_bytes)
                        
                    inside_file = False
                    current_file_path = None
                    continue
                
                if inside_file:
                    current_content.append(line)
                    
            print("Decompression terminee avec succes !")
            QtWidgets.QMessageBox.information(self, "Succès", "Extraction terminée avec succès !")
            
        except Exception as e:
            print(f"Erreur durant l'extraction : {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Erreur", f"Une erreur est survenue lors de l'extraction : {str(e)}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = UntardleApp()
    window.show()
    sys.exit(app.exec_())