import pyuff
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import numpy as np
from scipy.signal import savgol_filter
import control as ctrl
import matplotlib.pyplot as plt
import pandas as pd
from For_unv_files import Ui_MainWindow_For_unv_files
from MainWindow_theor_link_adding import Ui_MainWindow_theor_link_adding
from MainWindow_theor_link_adding import get_stability_margins
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar


def get_freq_resp(addr):
    """
    Функция, принимающая на вход адрес Excel документа, в котором, начиная со строки, где последовательно указаны "linear",
    "Amplidue" и "Phase", записаны данные о частотной харакретистике.
    Далее должны быть указаны частоты, амплитуды и фазы в соответствующих столбцах.
    Возвращает двумерный массив, где по по первый индекс соответствует величине(частота, амплитуда или фаза)
    а второй индекс соответствует номеру частоты, на которой исследовалась соответствующая характеристика
    """
    df = pd.read_excel(addr)
    start_index = df.loc[(df.iloc[:, 0] == "Linear") & (df.iloc[:, 1] == "Amplitude") & (df.iloc[:, 2] == "Phase")].index[0]
    df = df.iloc[start_index + 1:]
    hz_experiment = np.array(df.iloc[:, 0])
    hz_experiment = hz_experiment.astype('float64')
    amplitude_experiment = np.array(df.iloc[:, 1]).astype('float64')
    phase_experiment = np.array(df.iloc[:, 2]).astype('float64')
    freq_resp = np.array([hz_experiment, amplitude_experiment, phase_experiment])
    return freq_resp


def get_UNV_freq_resp(UNV_file, name):
    idx = None
    for i in range(UNV_file.get_n_sets()):
        try:
            if name == UNV_file.read_sets(i)['id4']:
                idx = i
                break
        except Exception:
            pass
    freqs = UNV_file.read_sets(idx)['x']
    amplitudes = abs(UNV_file.read_sets(idx)["data"])
    phases = np.rad2deg(np.angle(UNV_file.read_sets(idx)["data"]))
    freq_resp = np.array([freqs, amplitudes, phases])
    return freq_resp


def gcd(a, b):
    a = round(a * 1000)
    b = round(b * 1000)
    while b:
        a, b = b, a % b
    return round(a / 1000, 3)


class Ui_My_MainWindow(object):
    def setupUi(self, My_MainWindow):
        My_MainWindow.setObjectName("My_MainWindow")
        My_MainWindow.setEnabled(True)
        My_MainWindow.resize(1500, 850)
        self.my_centralwidget = QtWidgets.QWidget(My_MainWindow)
        self.my_centralwidget.setObjectName("my_centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.my_centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(540, 10, 521, 801))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        layout_for_tab_widget = QtWidgets.QVBoxLayout()
        layout_for_tab_widget.setContentsMargins(550, 5, 5, 5)
        self.my_centralwidget.setLayout(layout_for_tab_widget)
        self.tabWidget_for_graphs = QtWidgets.QTabWidget(self.my_centralwidget)
        self.tabWidget_for_graphs.setObjectName("tabWidget_for_graphs")

        self.tab_Bode = QtWidgets.QWidget()
        self.tab_Bode.setObjectName("tab_Bode")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_Bode)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_Bode = QtWidgets.QVBoxLayout()
        self.verticalLayout_Bode.setObjectName("verticalLayout_Bode")
        self.verticalLayout_3.addLayout(self.verticalLayout_Bode)

        self.canvas_for_Bode = FigureCanvas(plt.Figure(figsize=(15, 6)))
        self.verticalLayout_Bode.addWidget(self.canvas_for_Bode)
        self.ax_Bode = self.canvas_for_Bode.figure.subplots(nrows=2)

        self.toolbar = NavigationToolbar(self.canvas_for_Bode, My_MainWindow)
        self.verticalLayout_Bode.addWidget(self.toolbar)

        self.tabWidget_for_graphs.addTab(self.tab_Bode, "")

        self.tab_Nyquist = QtWidgets.QWidget()
        self.tab_Nyquist.setObjectName("tab_Nyquist")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_Nyquist)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_Nyquist = QtWidgets.QVBoxLayout()
        self.verticalLayout_Nyquist.setObjectName("verticalLayout_Nyquist")
        self.verticalLayout_2.addLayout(self.verticalLayout_Nyquist)

        self.canvas_for_Nyquist = FigureCanvas(plt.Figure(figsize=(15, 12)))
        self.verticalLayout_Nyquist.addWidget(self.canvas_for_Nyquist)
        self.ax_Nyquist = self.canvas_for_Nyquist.figure.subplots(nrows=1)
        self.init_graphs()
        self.toolbar = NavigationToolbar(self.canvas_for_Nyquist, My_MainWindow)
        self.verticalLayout_Nyquist.addWidget(self.toolbar)

        self.tabWidget_for_graphs.addTab(self.tab_Nyquist, "")
        layout_for_tab_widget.addWidget(self.tabWidget_for_graphs)

        self.widget = QtWidgets.QWidget(self.my_centralwidget)
        self.widget.setGeometry(QtCore.QRect(9, 9, 522, 801))
        self.widget.setObjectName("widget")
        self.tools_layout = QtWidgets.QVBoxLayout(self.widget)
        self.tools_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.tools_layout.setContentsMargins(5, 5, 5, 5)
        self.tools_layout.setObjectName("tools_layout")
        self.links_manager_layout = QtWidgets.QVBoxLayout()
        self.links_manager_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.links_manager_layout.setObjectName("links_manager_layout")
        self.listWidget_with_links_addrs = QtWidgets.QListWidget(self.widget)
        self.listWidget_with_links_addrs.setObjectName("listWidget_with_links_addrs")
        self.links_manager_layout.addWidget(self.listWidget_with_links_addrs)
        self.Links_managment_Buttons_Layout = QtWidgets.QHBoxLayout()
        self.Links_managment_Buttons_Layout.setObjectName("Links_managment_Buttons_Layout")
        self.delete_link_button = QtWidgets.QPushButton(self.widget)
        self.delete_link_button.setObjectName("delete_link_button")
        self.Links_managment_Buttons_Layout.addWidget(self.delete_link_button)
        self.add_theor_link_button = QtWidgets.QPushButton(self.widget)
        self.add_theor_link_button.setObjectName("add_theor_link_button")
        self.Links_managment_Buttons_Layout.addWidget(self.add_theor_link_button)
        self.add_link_button = QtWidgets.QPushButton(self.widget)
        self.add_link_button.setObjectName("add_link_button")
        self.Links_managment_Buttons_Layout.addWidget(self.add_link_button)
        self.links_manager_layout.addLayout(self.Links_managment_Buttons_Layout)
        self.tools_layout.addLayout(self.links_manager_layout)
        self.Graph_param_layout = QtWidgets.QVBoxLayout()
        self.Graph_param_layout.setObjectName("Graph_param_layout")
        self.min_freq_Layout = QtWidgets.QHBoxLayout()
        self.min_freq_Layout.setObjectName("min_freq_Layout")
        self.min_freq_label = QtWidgets.QLabel(self.widget)
        self.min_freq_label.setStyleSheet("font: 75 14pt \"MS Shell Dlg 2\";")
        self.min_freq_label.setObjectName("min_freq_label")
        self.min_freq_Layout.addWidget(self.min_freq_label)
        self.min_freq_doubleSpinBox = QtWidgets.QDoubleSpinBox(self.widget)
        self.min_freq_doubleSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.min_freq_doubleSpinBox.setSingleStep(0.1)
        self.min_freq_doubleSpinBox.setProperty("value", 1.0)
        self.min_freq_doubleSpinBox.setObjectName("min_freq_doubleSpinBox")
        self.min_freq_Layout.addWidget(self.min_freq_doubleSpinBox)
        self.Graph_param_layout.addLayout(self.min_freq_Layout)
        self.max_freq_Layout = QtWidgets.QHBoxLayout()
        self.max_freq_Layout.setObjectName("max_freq_Layout")
        self.max_freq_label = QtWidgets.QLabel(self.widget)
        self.max_freq_label.setStyleSheet("font: 75 14pt \"MS Shell Dlg 2\";")
        self.max_freq_label.setObjectName("max_freq_label")
        self.max_freq_Layout.addWidget(self.max_freq_label)
        self.max_freq_doubleSpinBox = QtWidgets.QDoubleSpinBox(self.widget)
        self.max_freq_doubleSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.max_freq_doubleSpinBox.setMaximum(999999.0)
        self.max_freq_doubleSpinBox.setProperty("value", 20.0)
        self.max_freq_doubleSpinBox.setObjectName("max_freq_doubleSpinBox")
        self.max_freq_Layout.addWidget(self.max_freq_doubleSpinBox)
        self.Graph_param_layout.addLayout(self.max_freq_Layout)
        self.filter_param_Layout = QtWidgets.QHBoxLayout()
        self.filter_param_Layout.setObjectName("filter_param_Layout")
        self.filter_param_label = QtWidgets.QLabel(self.widget)
        self.filter_param_label.setStyleSheet("font: 75 14pt \"MS Shell Dlg 2\";")
        self.filter_param_label.setObjectName("filter_param_label")
        self.filter_param_Layout.addWidget(self.filter_param_label)
        self.filter_param_spinBox = QtWidgets.QSpinBox(self.widget)
        self.filter_param_spinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.filter_param_spinBox.setMinimum(4)
        self.filter_param_spinBox.setMaximum(1000000000)
        self.filter_param_spinBox.setProperty("value", 4)
        self.filter_param_spinBox.setObjectName("filter_param_spinBox")
        self.filter_param_Layout.addWidget(self.filter_param_spinBox)
        self.Graph_param_layout.addLayout(self.filter_param_Layout)
        self.buttons_for_param_layout = QtWidgets.QHBoxLayout()
        self.buttons_for_param_layout.setObjectName("buttons_for_param_layout")
        self.button_result_w = QtWidgets.QPushButton(self.widget)
        self.button_result_w.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.button_result_w.setFont(font)
        self.button_result_w.setObjectName("button_result_w")
        self.buttons_for_param_layout.addWidget(self.button_result_w)
        self.checkBox_smooth = QtWidgets.QCheckBox(self.widget)
        self.checkBox_smooth.setEnabled(True)
        self.checkBox_smooth.setMaximumSize(QtCore.QSize(200, 16777215))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.checkBox_smooth.setFont(font)
        self.checkBox_smooth.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.checkBox_smooth.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkBox_smooth.setAutoFillBackground(False)
        self.checkBox_smooth.setChecked(True)
        self.checkBox_smooth.setObjectName("checkBox_smooth")
        self.buttons_for_param_layout.addWidget(self.checkBox_smooth)
        self.Graph_param_layout.addLayout(self.buttons_for_param_layout)
        self.tools_layout.addLayout(self.Graph_param_layout)
        self.Axes_names_layout = QtWidgets.QVBoxLayout()
        self.Axes_names_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.Axes_names_layout.setObjectName("Axes_names_layout")
        self.hor_A_Layout = QtWidgets.QHBoxLayout()
        self.hor_A_Layout.setObjectName("hor_A_Layout")
        self.hor_A_label = QtWidgets.QLabel(self.widget)
        self.hor_A_label.setStyleSheet("font: 75 14pt \"MS Shell Dlg 2\";")
        self.hor_A_label.setObjectName("hor_A_label")
        self.hor_A_Layout.addWidget(self.hor_A_label)
        self.lineEdit_horizontal_A = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_horizontal_A.setMaximumSize(QtCore.QSize(200, 16777215))
        self.lineEdit_horizontal_A.setText("Частота, Гц")
        self.lineEdit_horizontal_A.setObjectName("lineEdit_horizontal_A")
        self.hor_A_Layout.addWidget(self.lineEdit_horizontal_A)
        self.Axes_names_layout.addLayout(self.hor_A_Layout)
        self.vert_A_Layout = QtWidgets.QHBoxLayout()
        self.vert_A_Layout.setObjectName("vert_A_Layout")
        self.vart_A_label = QtWidgets.QLabel(self.widget)
        self.vart_A_label.setStyleSheet("font: 75 14pt \"MS Shell Dlg 2\";")
        self.vart_A_label.setObjectName("vart_A_label")
        self.vert_A_Layout.addWidget(self.vart_A_label)
        self.lineEdit_vertical_A = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_vertical_A.setMaximumSize(QtCore.QSize(200, 16777215))
        self.lineEdit_vertical_A.setText("Амплитуда")
        self.lineEdit_vertical_A.setObjectName("lineEdit_vertical_A")
        self.vert_A_Layout.addWidget(self.lineEdit_vertical_A)
        self.Axes_names_layout.addLayout(self.vert_A_Layout)
        self.hor_F_Layout = QtWidgets.QHBoxLayout()
        self.hor_F_Layout.setObjectName("hor_F_Layout")
        self.hor_F_label = QtWidgets.QLabel(self.widget)
        self.hor_F_label.setStyleSheet("font: 75 14pt \"MS Shell Dlg 2\";")
        self.hor_F_label.setObjectName("hor_F_label")
        self.hor_F_Layout.addWidget(self.hor_F_label)
        self.lineEdit_horizontal_F = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_horizontal_F.setMinimumSize(QtCore.QSize(200, 0))
        self.lineEdit_horizontal_F.setMaximumSize(QtCore.QSize(200, 16777215))
        self.lineEdit_horizontal_F.setText("Частота, Гц")
        self.lineEdit_horizontal_F.setObjectName("lineEdit_horizontal_F")
        self.hor_F_Layout.addWidget(self.lineEdit_horizontal_F)
        self.Axes_names_layout.addLayout(self.hor_F_Layout)
        self.vert_F_Layout = QtWidgets.QHBoxLayout()
        self.vert_F_Layout.setObjectName("vert_F_Layout")
        self.ver_F_label = QtWidgets.QLabel(self.widget)
        self.ver_F_label.setStyleSheet("font: 75 14pt \"MS Shell Dlg 2\";")
        self.ver_F_label.setObjectName("ver_F_label")
        self.vert_F_Layout.addWidget(self.ver_F_label)
        self.lineEdit_vertical_F = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_vertical_F.setMaximumSize(QtCore.QSize(200, 16777215))
        self.lineEdit_vertical_F.setText("Фаза, град")
        self.lineEdit_vertical_F.setObjectName("lineEdit_vertical_F")
        self.vert_F_Layout.addWidget(self.lineEdit_vertical_F)
        self.Axes_names_layout.addLayout(self.vert_F_Layout)
        self.buttons_for_graphs_Layout = QtWidgets.QHBoxLayout()
        self.buttons_for_graphs_Layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.buttons_for_graphs_Layout.setObjectName("buttons_for_graphs_Layout")
        self.save_graphs_button = QtWidgets.QPushButton(self.widget)
        self.save_graphs_button.setMinimumSize(QtCore.QSize(0, 23))
        self.save_graphs_button.setMaximumSize(QtCore.QSize(150, 16777215))
        self.save_graphs_button.setObjectName("save_graphs_button")
        self.buttons_for_graphs_Layout.addWidget(self.save_graphs_button)
        self.apply_axes_params_button = QtWidgets.QPushButton(self.widget)
        self.apply_axes_params_button.setMaximumSize(QtCore.QSize(150, 16777215))
        self.apply_axes_params_button.setObjectName("apply_axes_params_button")
        self.buttons_for_graphs_Layout.addWidget(self.apply_axes_params_button)
        self.Axes_names_layout.addLayout(self.buttons_for_graphs_Layout)
        self.tools_layout.addLayout(self.Axes_names_layout)
        self.clear_graphs_button = QtWidgets.QPushButton(self.widget)
        self.clear_graphs_button.setObjectName("clear_graphs_button")
        self.tools_layout.addWidget(self.clear_graphs_button)
        My_MainWindow.setCentralWidget(self.my_centralwidget)
        # Отдельно вызываем функцию инициализирующую обработку сигналов и событий
        self.theor_links_dict = dict()
        self.UNV_FRF_dict = dict()
        self.temp_UNV_file = None
        self.add_functions()
        self.retranslateUi_main(My_MainWindow)
        self.tabWidget_for_graphs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(My_MainWindow)

    def init_graphs(self):
        self.ax_Bode[0].set_title('Амплитудно-частотная характеристика', size=10)
        self.ax_Bode[0].set_ylabel("Амплитуда", size=10)
        self.ax_Bode[0].set_xlabel("Частота, Гц", size=10)
        self.ax_Bode[1].set_title("Фазо-частотная характеристика", size=10)
        self.ax_Bode[1].set_ylabel("Фаза, град", size=10)
        self.ax_Bode[1].set_xlabel("Частота, Гц", size=10)
        self.ax_Bode[0].grid(True)
        self.ax_Bode[1].grid(True)
        self.canvas_for_Bode.figure.subplots_adjust(hspace=0.250)
        self.ax_Nyquist.set_title('Диаграмма Найквиста', size=10)
        self.ax_Nyquist.set_ylabel('Im $W(i\omega)$', size=10)
        self.ax_Nyquist.set_xlabel('Re $W(i\omega)$', size=10)
        self.ax_Nyquist.grid(True)
        self.canvas_for_Nyquist.figure.subplots_adjust(hspace=0.250)
        self.build_Nyquist_limitations()

    def build_Nyquist_limitations(self):
        self.ax_Nyquist.set_xlim([-1, 1])
        self.ax_Nyquist.set_ylim([-1, 1])
        self.ax_Nyquist.plot(np.cos(np.linspace(-np.pi / 2, np.pi / 2, 50)) * 0.3,
                             np.sin(np.linspace(-np.pi / 2, np.pi / 2, 50)) * 0.3, color="black")
        self.ax_Nyquist.plot([0] * 2, np.linspace(0.3, 1, 2), color="black")
        self.ax_Nyquist.plot([0] * 2, np.linspace(-0.3, -1, 2), color="black")
        self.ax_Nyquist.plot(np.cos(np.linspace(-np.pi / 3, np.pi / 3, 50)) * 0.5,
                             np.sin(np.linspace(-np.pi / 3, np.pi / 3, 50)) * 0.5, color="black")
        self.ax_Nyquist.plot(np.linspace(0.5, 3, 50) * np.cos(np.pi / 3), np.linspace(0.5, 3, 50) * np.sin(np.pi / 3),
                             color="black")
        self.ax_Nyquist.plot(np.linspace(0.5, 3, 50) * np.cos(np.pi / 3), np.linspace(0.5, 3, 50) * np.sin(-np.pi / 3),
                             color="black")
        self.canvas_for_Nyquist.draw()

    def add_functions(self):
        self.add_link_button.clicked.connect(lambda: self.adding_link())
        self.clear_graphs_button.clicked.connect(lambda: self.clear_graphs())
        self.delete_link_button.clicked.connect(lambda: self.delete_link())
        self.button_result_w.clicked.connect(lambda: self.print_result_graph())
        self.save_graphs_button.clicked.connect(lambda: self.save_graphs_function())
        self.apply_axes_params_button.clicked.connect(lambda: self.apply_labels())
        self.add_theor_link_button.clicked.connect(lambda: self.call_adding_theor_window())

    # Функция удаления графиков с осей
    def clear_graphs(self):
        self.ax_Bode[0].cla()
        self.ax_Bode[1].cla()
        self.ax_Nyquist.cla()
        self.init_graphs()
        self.canvas_for_Bode.draw()
        self.canvas_for_Nyquist.draw()

    # Добавление звена
    def adding_link(self):
        file_addr = QtWidgets.QFileDialog.getOpenFileName()[0]
        if file_addr != "":
            if file_addr[-3:] != "uff" and file_addr[-3:] != "unv":
                self.listWidget_with_links_addrs.addItem(file_addr)
            elif file_addr[-3:] == "uff" or file_addr[-3:] == "unv":
                self.call_adding_link_from_UNV_window(file_addr)

    def call_adding_link_from_UNV_window(self, addr):
        self.temp_UNV_file = pyuff.UFF(addr)
        self.new_widnow_for_UNV = QtWidgets.QMainWindow()
        self.new_ui_for_UNV = Ui_MainWindow_For_unv_files()
        self.new_ui_for_UNV.setupUi(self.new_widnow_for_UNV, self, self.temp_UNV_file)
        self.new_widnow_for_UNV.show()

    def add_FRF_from_UNV_function(self, id4):
        self.UNV_FRF_dict[id4] = get_UNV_freq_resp(self.temp_UNV_file, id4)
        self.listWidget_with_links_addrs.addItem(id4)

    def call_adding_theor_window(self):
        self.new_widnow = QtWidgets.QMainWindow()
        self.new_ui = Ui_MainWindow_theor_link_adding()
        self.new_ui.setupUi(self.new_widnow, self)
        self.new_widnow.show()

    def add_theor_link_function(self):
        """
        Функция, осуществляющая передачу информации о заданной теоретически передаточной функции в список с передаточными функциями
        Новая функция, если имеет имя, уже встречающееся в списке, заменяет старую, а в списке имён новых не добавляется
        Если такой функции нет, создаётся передаточная функция, информация по которой хранится в словаре, а взаимодействие с ней
        осуществляется через список передаточных функций
        """
        try:
            numerator_list = self.new_ui.lineEdit_numerator.text().split()
            denominator_list = self.new_ui.lineEdit_denominator.text().split()
            if len(numerator_list) * len(denominator_list) == 0:
                raise Exception
            for i in range(len(numerator_list)):
                numerator_list[i] = float(numerator_list[i])
            for i in range(len(denominator_list)):
                denominator_list[i] = float(denominator_list[i])
            name = self.new_ui.lineEdit_name_theor_link.text()
            self.theor_links_dict[name] = ctrl.tf(numerator_list, denominator_list)
            founded = False
            for i in range(self.listWidget_with_links_addrs.count()):
                if self.listWidget_with_links_addrs.item(i).text()[3:] == name:
                    founded = True
            if not founded:
                self.listWidget_with_links_addrs.addItem("T: " + name)
        except Exception:
            pass

    # Удаление звена
    def delete_link(self):
        clicked_index = self.listWidget_with_links_addrs.currentRow()
        name = self.listWidget_with_links_addrs.takeItem(clicked_index).text()
        if name[0] == "T":
            del self.theor_links_dict[name[3:]]
        elif name[0:6] == "Record":
            del self.UNV_FRF_dict[name]

    # Функция построения диаграмм произведения звеньев
    def print_result_graph(self):
        if self.listWidget_with_links_addrs.count() >= 1:
            theoretical_w_list = []
            list_with_frequency_responses = []
            for x in range(self.listWidget_with_links_addrs.count()):
                addr = self.listWidget_with_links_addrs.item(x).text()
                if addr[0] != "T" and addr[0:6] != "Record":
                    list_with_frequency_responses.append(get_freq_resp(addr))
                elif addr[0] == "T":
                    theoretical_w_list.append(self.theor_links_dict[addr[3:]])
                elif addr[0:6] == "Record":
                    list_with_frequency_responses.append(self.UNV_FRF_dict[addr])
            correct_points = self.get_correct_interval(list_with_frequency_responses)
            result_freq_resp = self.get_result_freq_resp(correct_points, list_with_frequency_responses,
                                                         theoretical_w_list)
            margines = get_stability_margins(result_freq_resp[1], result_freq_resp[2])
            self.adding_graph(result_freq_resp[0], result_freq_resp[1], result_freq_resp[2])
            margines_message = QtWidgets.QMessageBox()
            margines_message.setIcon(QtWidgets.QMessageBox.Information)
            margines_message.setWindowTitle("Запасы устойчивости")
            if margines[0] != "None":
                margines_message.setText(
                    "Запас по амплитуде = {}\n Запас по фазе = {}".format(margines[0], margines[1]))
            else:
                margines_message.setText("Система неустойчива")
            margines_message.setStandardButtons(QtWidgets.QMessageBox.Ok)
            margines_message.exec_()
        else:
            print("Введите какие-либо данные для отображения")

    # Функция нахождения корректного множества точек
    def get_correct_interval(self, freq_resps):
        if self.min_freq_doubleSpinBox.value() > self.max_freq_doubleSpinBox.value():
            my_max = self.min_freq_doubleSpinBox.value()
            my_min = self.max_freq_doubleSpinBox.value()
            self.min_freq_doubleSpinBox.setValue(my_min)
            self.max_freq_doubleSpinBox.setValue(my_max)
        if len(freq_resps) > 0:
            lowest_freq = max([freq_resps[i][0][0] for i in range(len(freq_resps))])
            lowest_freq = max(lowest_freq, self.min_freq_doubleSpinBox.value())
            highest_freq = min([freq_resps[i][0][-1] for i in range(len(freq_resps))])
            highest_freq = min(highest_freq, self.max_freq_doubleSpinBox.value())
            temp_gcd = freq_resps[0][0][1] - freq_resps[0][0][0]
            for resp in freq_resps:
                temp_gcd = gcd(temp_gcd, abs(resp[0][1] - resp[0][0]))
            try:
                if lowest_freq <= highest_freq:
                    num_points = round((highest_freq - lowest_freq) / temp_gcd) + 1
                    correct_points = np.linspace(lowest_freq, highest_freq, int(num_points))
                    return correct_points
                else:
                    raise ValueError
            except ValueError:
                print(ValueError("Отсутствуют исследуемые точки"))
                return [0]
        else:
            return np.linspace(self.min_freq_doubleSpinBox.value(), self.max_freq_doubleSpinBox.value(), 101)

    def get_result_freq_resp(self, correct_points, freq_resps, theoretical_w_list):
        try:
            if len(freq_resps) == 0 and len(theoretical_w_list) == 0:
                raise ValueError
        except ValueError:
            print("Отсутствуют данные для построения графика")
            return [0], [0], [0]
        new_freq_resp_amplitudes = []
        new_freq_resp_phases = []
        if len(freq_resps) != 0:
            # переводим фазу в диапаздон от 0 до -360
            for i in range(len(freq_resps)):
                for j in range(len(freq_resps[i][2])):
                    phase = freq_resps[i][2][j]
                    while not (-360 < phase <= 0):
                        if phase > 0:
                            phase -= 360
                        else:
                            phase += 360
                    freq_resps[i][2][j] = phase
            # Устранение "проблемных" мест в фазах
            phases_to_fix = list()
            the_least = 10000
            the_biggest = 0
            for i in range(len(freq_resps)):
                for j in range(len(freq_resps[i][2]) - 1):
                    delta_grad_by_delta_omega = (freq_resps[i][2][j + 1] - freq_resps[i][2][j]) / (
                                freq_resps[i][0][j + 1] - freq_resps[i][0][j])
                    if delta_grad_by_delta_omega >= 900:
                        phases_to_fix.append((freq_resps[i][0][j], freq_resps[i][0][j + 1], freq_resps[i][2][j],
                                              freq_resps[i][2][j + 1], i))
                        if phases_to_fix[-1][0] < the_least:
                            the_least = phases_to_fix[-1][0]
                        if phases_to_fix[-1][1] > the_biggest:
                            the_biggest = phases_to_fix[-1][1]

            for i in range(len(freq_resps)):
                new_freq_resp_amplitudes.append(np.interp(correct_points, freq_resps[i][0], freq_resps[i][1]))
                new_freq_resp_phases.append(np.interp(correct_points, freq_resps[i][0], freq_resps[i][2]))

            for i in range(len(correct_points)):
                if the_least > correct_points[i] or the_biggest < correct_points[i]:
                    continue
                for j in range(len(phases_to_fix)):
                    if phases_to_fix[j][0] <= correct_points[i] <= phases_to_fix[j][1]:
                        new_freq_resp_phases[phases_to_fix[j][4]][i] = phases_to_fix[j][2]

            result_amplitude = new_freq_resp_amplitudes[0].copy()
            result_phase = new_freq_resp_phases[0].copy()
            for i in range(1, len(new_freq_resp_amplitudes)):
                result_amplitude *= new_freq_resp_amplitudes[i]
                result_phase += new_freq_resp_phases[i]
            for temp_w_theor in theoretical_w_list:
                temp_amplidudes, temp_phases, _ = temp_w_theor.freqresp(correct_points)
                result_amplitude *= temp_amplidudes
                for i in range(len(temp_phases)):
                    temp_phases[i] = np.rad2deg(temp_phases[i])
                    while not (-360 <= temp_phases[i] <= 0):
                        if temp_phases[i] >= 0:
                            temp_phases[i] -= 360
                        else:
                            temp_phases[i] += 360
                result_phase += temp_phases
            for i in range(len(result_phase)):
                while not (-360 <= result_phase[i] <= 0):
                    if result_phase[i] >= 0:
                        result_phase[i] -= 360
                    else:
                        result_phase[i] += 360
            return correct_points, result_amplitude, result_phase
        else:
            result_amplitude = [1 for i in range(len(correct_points))]
            result_phase = [0 for i in range(len(correct_points))]
            for temp_w_theor in theoretical_w_list:
                temp_amplidudes, temp_phases, _ = temp_w_theor.freqresp(correct_points)
                result_amplitude *= temp_amplidudes
                for i in range(len(temp_phases)):
                    temp_phases[i] = np.rad2deg(temp_phases[i])
                    while not (-360 <= temp_phases[i] <= 0):
                        if temp_phases[i] >= 0:
                            temp_phases[i] -= 360
                        else:
                            temp_phases[i] += 360
                result_phase += temp_phases
            for i in range(len(result_phase)):
                while not (-360 <= result_phase[i] <= 0):
                    if result_phase[i] >= 0:
                        result_phase[i] -= 360
                    else:
                        result_phase[i] += 360
            return correct_points, result_amplitude, result_phase

    # Функция добавления графика на холст
    def adding_graph(self, x=[0], y1=[0], y2=[0]):
        if not self.checkBox_smooth.isChecked():
            self.ax_Bode[0].plot(x, y1)
            self.ax_Bode[1].plot(x, y2)
        else:
            self.ax_Bode[0].plot(x, savgol_filter(y1, self.filter_param_spinBox.value(), 3))
            self.ax_Bode[1].plot(x, y2)
        self.canvas_for_Bode.draw()
        self.ax_Nyquist.plot(y1 * np.cos(np.deg2rad(y2)),
                             y1 * np.sin(np.deg2rad(y2)))
        self.canvas_for_Nyquist.draw()

    # Функция изменения подписей осей
    def apply_labels(self):
        hor_A = self.lineEdit_horizontal_A.text()
        ver_A = self.lineEdit_vertical_A.text()
        hor_F = self.lineEdit_horizontal_F.text()
        ver_F = self.lineEdit_vertical_F.text()
        self.ax_Bode[0].set_xlabel(hor_A)
        self.ax_Bode[0].set_ylabel(ver_A)
        self.ax_Bode[1].set_xlabel(hor_F)
        self.ax_Bode[1].set_ylabel(ver_F)
        self.canvas_for_Bode.draw()

    def save_graphs_function(self):
        temp_size = self.canvas_for_Bode.figure.get_size_inches()
        self.canvas_for_Bode.figure.set_size_inches(16.5 / 2.54, 21 / 2.54)
        self.canvas_for_Bode.figure.subplots_adjust(hspace=0.350)
        self.canvas_for_Bode.figure.savefig("Bode.png")
        self.canvas_for_Bode.figure.set_size_inches(temp_size)
        self.canvas_for_Bode.draw()

        temp_size = self.canvas_for_Nyquist.figure.get_size_inches()
        self.canvas_for_Nyquist.figure.set_size_inches(16.5 / 2.54, 16.5 / 2.54)
        self.canvas_for_Nyquist.figure.subplots_adjust(hspace=0.350)
        self.canvas_for_Nyquist.figure.savefig("Nyquist.png")
        self.canvas_for_Nyquist.figure.set_size_inches(temp_size)
        self.canvas_for_Nyquist.draw()

    def retranslateUi_main(self, My_MainWindow):
        _translate = QtCore.QCoreApplication.translate
        My_MainWindow.setWindowTitle(_translate("My_MainWindow", "Links product counter"))
        self.delete_link_button.setText(_translate("My_MainWindow", "Удалить звено"))
        self.clear_graphs_button.setText(_translate("My_MainWindow", "Очистить графики"))
        self.add_theor_link_button.setText(_translate("My_MainWindow", "Добавить теор. звено"))
        self.add_link_button.setText(_translate("My_MainWindow", "Добавить звено"))
        self.min_freq_label.setText(_translate("My_MainWindow",
                                               "<html><head/><body><p align=\"center\">Минимальная частота, Гц</p></body></html>"))
        self.max_freq_label.setText(_translate("My_MainWindow",
                                               "<html><head/><body><p align=\"center\">Максимальная частота, Гц</p></body></html>"))
        self.filter_param_label.setText(
            _translate("My_MainWindow",
                       "<html><head/><body><p align=\"center\">Параметр сглаживающего фильтра</p></body></html>"))
        self.button_result_w.setText(_translate("My_MainWindow", "Результат"))
        self.checkBox_smooth.setText(_translate("My_MainWindow", "Сглаживание графика АЧХ"))
        self.hor_A_label.setText(_translate("My_MainWindow",
                                            "<html><head/><body><p align=\"center\">Подпись горизонтальной оси АЧХ</p></body></html>"))
        self.vart_A_label.setText(_translate("My_MainWindow",
                                             "<html><head/><body><p align=\"center\">Подпись вертикальной оси АЧХ</p></body></html>"))
        self.hor_F_label.setText(_translate("My_MainWindow",
                                            "<html><head/><body><p align=\"center\">Подпись горизонтальной оси ФЧХ</p></body></html>"))
        self.ver_F_label.setText(_translate("My_MainWindow",
                                            "<html><head/><body><p align=\"center\">Подпись вертикальной оси ФЧХ</p></body></html>"))
        self.save_graphs_button.setText(_translate("My_MainWindow", "Сохранить графики"))
        self.apply_axes_params_button.setText(_translate("My_MainWindow", "Применить"))
        self.tabWidget_for_graphs.setTabText(self.tabWidget_for_graphs.indexOf(self.tab_Bode),
                                             _translate("My_MainWindow", "Диаграмма Боде"))
        self.tabWidget_for_graphs.setTabText(self.tabWidget_for_graphs.indexOf(self.tab_Nyquist),
                                             _translate("My_MainWindow", "Диаграмма Найквиста"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_My_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())