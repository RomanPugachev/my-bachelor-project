import pyuff
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTreeWidgetItem

class Ui_MainWindow_For_unv_files(object):
    def setupUi(self, MainWindow_For_unv_files, parent=None, unv_file=None):
        MainWindow_For_unv_files.setObjectName("MainWindow_For_unv_files")
        MainWindow_For_unv_files.resize(800, 497)
        self.centralwidget = QtWidgets.QWidget(MainWindow_For_unv_files)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_main = QtWidgets.QVBoxLayout()
        self.verticalLayout_main.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.verticalLayout_main.setObjectName("verticalLayout_main")
        self.TreeWidget_with_FRF = QtWidgets.QTreeWidget(self.centralwidget)
        self.TreeWidget_with_FRF.setObjectName("listWidget_with_FRF")
        self.verticalLayout_main.addWidget(self.TreeWidget_with_FRF)
        self.horizontalLayout_buttons = QtWidgets.QHBoxLayout()
        self.horizontalLayout_buttons.setObjectName("horizontalLayout_buttons")
        self.pushButton_close_window = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.pushButton_close_window.setFont(font)
        self.pushButton_close_window.setTabletTracking(False)
        self.pushButton_close_window.setStyleSheet("color: rgb(255, 255, 255);\n"
                                                   "background-color: rgb(255, 0, 0);")
        self.pushButton_close_window.setObjectName("pushButton_close_window")
        self.horizontalLayout_buttons.addWidget(self.pushButton_close_window)
        self.pushButton_add_FRF = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_add_FRF.setFont(font)
        self.pushButton_add_FRF.setStyleSheet("background-color: rgb(0, 255, 0);\n"
                                              "color:rgb(0, 0, 0)")
        self.pushButton_add_FRF.setObjectName("pushButton_add_FRF")
        self.horizontalLayout_buttons.addWidget(self.pushButton_add_FRF)
        self.verticalLayout_main.addLayout(self.horizontalLayout_buttons)
        self.verticalLayout_2.addLayout(self.verticalLayout_main)
        MainWindow_For_unv_files.setCentralWidget(self.centralwidget)
        self.add_functions(MainWindow_For_unv_files)
        self.retranslateUi(MainWindow_For_unv_files)
        QtCore.QMetaObject.connectSlotsByName(MainWindow_For_unv_files)
        self.parent = parent
        self.build_tree(unv_file)

    def build_tree(self, unv_file):
        # Построение дерева
        self.TreeWidget_with_FRF.setHeaderHidden(True)
        self.tree_dict = {}
        for i in range(unv_file.get_n_sets()):
            temp_set = unv_file.read_sets(i)
            try:
                temp_name = temp_set['id4']
                temp_category = temp_set['id1'].split()[0]
            except Exception:
                continue
            temp_num = temp_name.split()[-1]
            if "_" in temp_num:
                if temp_num not in self.tree_dict.keys():
                    self.tree_dict[temp_num] = {}
                if temp_category not in self.tree_dict[temp_num].keys():
                    self.tree_dict[temp_num][temp_category] = list()
                self.tree_dict[temp_num][temp_category].append(temp_name)
            else:
                continue
        for temp_num in self.tree_dict.keys():
            temp_num_item = QTreeWidgetItem([temp_num])
            for temp_category in self.tree_dict[temp_num].keys():
                temp_category_item = QTreeWidgetItem([temp_category])
                for temp_name in self.tree_dict[temp_num][temp_category]:
                    temp_name_item = QTreeWidgetItem([temp_name])
                    temp_category_item.addChild(temp_name_item)
                temp_num_item.addChild(temp_category_item)
            self.TreeWidget_with_FRF.addTopLevelItem(temp_num_item)

    def add_functions(self, MainWindow_For_unv_files):
        self.pushButton_add_FRF.clicked.connect(lambda: self.add_FRF(self.parent))
        self.pushButton_close_window.clicked.connect(lambda: MainWindow_For_unv_files.close())

    def add_FRF(self, parent):
        current_item = self.TreeWidget_with_FRF.currentItem()
        if current_item.text(0)[:6] == "Record":
            parent.add_FRF_from_UNV_function(current_item.text(0))

    def retranslateUi(self, MainWindow_For_unv_files):
        _translate = QtCore.QCoreApplication.translate
        MainWindow_For_unv_files.setWindowTitle(
            _translate("MainWindow_For_unv_files", "Добавление звена из файла универсального формата"))
        self.pushButton_close_window.setText(_translate("MainWindow_For_unv_files", "Закрыть"))
        self.pushButton_add_FRF.setText(_translate("MainWindow_For_unv_files", "Добавить передаточную функцию"))