import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QTableView, QLineEdit, QLabel, QListWidget, QListWidgetItem,
    QComboBox, QMessageBox, QSplitter, QAbstractItemView, QTreeView
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant
import re
class PandasTableModel(QAbstractTableModel):
    def __init__(self, df):
        super().__init__()
        self._df = df

    def rowCount(self, parent=QModelIndex()):
        return 0 if self._df is None else len(self._df)

    def columnCount(self, parent=QModelIndex()):
        return 0 if self._df is None else self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or self._df is None:
            return QVariant()
        if role == Qt.DisplayRole:
            value = self._df.iat[index.row(), index.column()]
            return str(value)
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if self._df is None:
            return QVariant()
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._df.columns[section])
            else:
                return str(section)
        return QVariant()
from esamina_excel import esamina_excel, raggruppa_per_lettera_tariffa

class ExcelSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Search & Category Tool")
        self.resize(1400, 800)
        self.df = None
        self.filtered_df = None
        self.selected_df = pd.DataFrame()
        self.categories = {}
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        # --- Barra superiore con controlli ---
        controls_layout = QHBoxLayout()
        self.load_btn = QPushButton("Carica Excel")
        self.load_btn.clicked.connect(self.load_excel)
        controls_layout.addWidget(self.load_btn)
        controls_layout.addSpacing(20)
        controls_layout.addWidget(QLabel("Ricerca:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cerca su tutti i campi...")
        self.search_input.textChanged.connect(self.apply_filter)
        controls_layout.addWidget(self.search_input)
        controls_layout.addWidget(QLabel("Colonna:"))
        self.column_filter = QComboBox()
        self.column_filter.addItem("Tutte le colonne")
        self.column_filter.currentIndexChanged.connect(self.apply_filter)
        controls_layout.addWidget(self.column_filter)
        controls_layout.addStretch()
        self.rows_label = QLabel()
        controls_layout.addWidget(self.rows_label)

        # --- Splitter centrale ---
        splitter = QSplitter(Qt.Horizontal)
        # TreeView a sinistra
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.clicked.connect(self.on_tree_selected)
        tree_layout = QVBoxLayout()
        tree_layout.addWidget(QLabel("Gerarchia Tariffa"))
        tree_layout.addWidget(self.tree_view)
        tree_widget = QWidget()
        tree_widget.setLayout(tree_layout)
        splitter.addWidget(tree_widget)

        # Tabella centrale
        table_layout = QVBoxLayout()
        table_layout.addWidget(QLabel("Dati Excel"))
        table_layout.addWidget(self.table_view)
        table_widget = QWidget()
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Selezionati e categorie a destra
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Selezionati"))
        right_layout.addWidget(self.selected_view)
        right_layout.addWidget(QLabel("Categorie"))
        right_layout.addWidget(self.category_list)
        btn_layout = QVBoxLayout()
        self.add_btn = QPushButton("Aggiungi selezionati →")
        self.add_btn.clicked.connect(self.add_selected)
        self.create_cat_btn = QPushButton("Crea categoria")
        self.create_cat_btn.clicked.connect(self.create_category)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.create_cat_btn)
        right_layout.addLayout(btn_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        splitter.setSizes([200, 800, 300])
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.update_rows_label()
        self.tree_model = None

    def load_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona file Excel", "data", "Excel Files (*.xlsx *.xls)")
        if not file_path:
            return
        df = esamina_excel(file_path)
        if df is None:
            QMessageBox.warning(self, "Errore", "Impossibile caricare il file Excel.")
            return
        self.df = df.reset_index(drop=True)
        self.filtered_df = self.df.copy()
        self.selected_df = pd.DataFrame(columns=self.df.columns)
        self.update_table()
        self.update_column_filter()
        self.category_list.clear()
        self.categories = {}
        self.build_tree_model()
    def build_tree_model(self):
        # Costruisce la gerarchia dei codici tariffa: primo livello le lettere (E01, EL, ...)
        if self.df is None or 'TARIFFA' not in self.df.columns:
            self.tree_view.setModel(None)
            return
        model = QStandardItemModel()
        root = model.invisibleRootItem()
        # Dizionario nidificato: {E01: {001: {001: [record, ...]}}}
        tree = {}
        for idx, row in self.df.iterrows():
            codice = row['TARIFFA']
            # Estrai livelli: E01, 001, 001
            match = re.match(r'PUG\d{4}/\d+\.([A-Z]+\d+)\.(\d+)\.(\d+)', codice)
            if not match:
                continue
            l1, l2, l3 = match.groups()
            tree.setdefault(l1, {}).setdefault(l2, {}).setdefault(l3, []).append(idx)
        for l1 in sorted(tree.keys()):
            item1 = QStandardItem(l1)
            for l2 in sorted(tree[l1].keys()):
                item2 = QStandardItem(l2)
                for l3 in sorted(tree[l1][l2].keys()):
                    item3 = QStandardItem(l3)
                    # Salva gli indici dei record come data
                    item3.setData(tree[l1][l2][l3], Qt.UserRole)
                    item2.appendRow(item3)
                item1.appendRow(item2)
            root.appendRow(item1)
        self.tree_model = model
        self.tree_view.setModel(model)
        self.tree_view.expandToDepth(1)

    def on_tree_selected(self, index):
        # Filtra tutte le voci che iniziano con il codice del nodo selezionato
        item = self.tree_model.itemFromIndex(index)
        codice = []
        while item and item.parent() is not None:
            codice.insert(0, item.text())
            item = item.parent()
        if not codice:
            self.filtered_df = self.df.copy()
        else:
            # Costruisci il prefisso da cercare
            # Esempio: ['E01', '001', '001'] -> 'E01.001.001'
            prefisso = '.'.join(codice)
            mask = self.df['TARIFFA'].str.contains(rf'\.{prefisso}$') | self.df['TARIFFA'].str.contains(rf'\.{prefisso}\.') | self.df['TARIFFA'].str.contains(rf'/{prefisso}\.')
            self.filtered_df = self.df[mask].copy()
        self.update_table()

    def update_table(self):
        if self.filtered_df is None:
            return
        model = PandasTableModel(self.filtered_df)
        self.table_view.setModel(model)
        self.table_view.resizeColumnsToContents()
        self.update_rows_label()

        # Update selected table (può restare QStandardItemModel perché pochi record)
        sel_model = QStandardItemModel(self.selected_df.shape[0], self.selected_df.shape[1])
        sel_model.setHorizontalHeaderLabels(self.selected_df.columns)
        for row in range(self.selected_df.shape[0]):
            for col in range(self.selected_df.shape[1]):
                value = str(self.selected_df.iat[row, col])
                sel_model.setItem(row, col, QStandardItem(value))
        self.selected_view.setModel(sel_model)
        self.selected_view.resizeColumnsToContents()

    def update_rows_label(self):
        if self.df is not None and self.filtered_df is not None:
            self.rows_label.setText(f"Righe filtrate: {len(self.filtered_df)} / Totali: {len(self.df)}")
        else:
            self.rows_label.setText("")

    def update_column_filter(self):
        self.column_filter.clear()
        self.column_filter.addItem("Tutte le colonne")
        if self.df is not None:
            for col in self.df.columns:
                self.column_filter.addItem(col)

    def apply_filter(self):
        if self.df is None:
            return
        text = self.search_input.text().lower()
        col = self.column_filter.currentText()
        if not text:
            self.filtered_df = self.df.copy()
        else:
            if col == "Tutte le colonne":
                mask = self.df.apply(lambda row: row.astype(str).str.lower().str.contains(text).any(), axis=1)
            else:
                mask = self.df[col].astype(str).str.lower().str.contains(text)
            self.filtered_df = self.df[mask].copy()
        self.update_table()

    def add_selected(self):
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            return
        rows = [self.filtered_df.iloc[i.row()] for i in indexes]
        new_df = pd.DataFrame(rows)
        self.selected_df = pd.concat([self.selected_df, new_df]).drop_duplicates().reset_index(drop=True)
        self.update_table()

    def create_category(self):
        name, ok = QFileDialog.getSaveFileName(self, "Nome categoria", "", "Categoria (*.cat)")
        if ok and name:
            cat_name = os.path.splitext(os.path.basename(name))[0]
            self.categories[cat_name] = self.selected_df.copy()
            self.category_list.addItem(cat_name)
            QMessageBox.information(self, "Categoria creata", f"Categoria '{cat_name}' creata con {len(self.selected_df)} record.")

    def show_category(self, item: QListWidgetItem):
        cat_name = item.text()
        if cat_name in self.categories:
            self.selected_df = self.categories[cat_name].copy()
            self.update_table()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExcelSearchApp()
    window.show()
    sys.exit(app.exec_())
