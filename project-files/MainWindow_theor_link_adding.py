from PyQt5 import QtCore, QtGui, QtWidgets


def get_stability_margins(amplitudes, phases):
    amp_margine, phase_margine = None, None
    indexes_amplitude_margine = []
    for i in range(1, len(phases)):
        if abs(phases[i] - phases[i - 1]) >= 180:
            indexes_amplitude_margine.append(i)
    tmp_max = 0
    for index in indexes_amplitude_margine:
        if amplitudes[index] > tmp_max:
            tmp_max = amplitudes[index]
    if tmp_max > 1:
        return ("None", "None")
    else:
        amp_margine = 1 - tmp_max
    indexes_phase_margine = []
    for i in range(1, len(amplitudes)):
        if (amplitudes[i] >= 1 and amplitudes[i - 1] <= 1) or (amplitudes[i - 1] >= 1 and amplitudes[i] <= 1):
            indexes_phase_margine.append(i)
    tmp_min = 0
    for index in indexes_phase_margine:
        if phases[index] < tmp_min:
            tmp_min = phases[index]
    phase_margine = 360 + tmp_min
    return str(round(amp_margine, 2)), str(round(phase_margine))


class Ui_MainWindow_theor_link_adding(object):
    """
    Окно, вызывающееся из основного окна, предназначенное для введения теоретической передаточной функци и её добавления в список
    к другим передаточным функциям
    """
    def setupUi(self, MainWindow_theor_link_adding, parent=None):
        MainWindow_theor_link_adding.setObjectName("MainWindow_theor_link_adding")
        MainWindow_theor_link_adding.resize(500, 300)
        MainWindow_theor_link_adding.setMinimumSize(QtCore.QSize(500, 300))
        MainWindow_theor_link_adding.setMaximumSize(QtCore.QSize(500, 300))
        self.centralwidget = QtWidgets.QWidget(MainWindow_theor_link_adding)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(40, 84, 411, 41))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_numerator = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_numerator.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_numerator.setObjectName("horizontalLayout_numerator")
        self.label_numerator = QtWidgets.QLabel(self.layoutWidget)
        self.label_numerator.setObjectName("label_numerator")
        self.horizontalLayout_numerator.addWidget(self.label_numerator)
        self.lineEdit_numerator = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_numerator.setObjectName("lineEdit_numerator")
        self.horizontalLayout_numerator.addWidget(self.lineEdit_numerator)
        self.layoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_2.setGeometry(QtCore.QRect(40, 130, 411, 41))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.horizontalLayout_denominator = QtWidgets.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_denominator.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_denominator.setObjectName("horizontalLayout_denominator")
        self.label_denominator = QtWidgets.QLabel(self.layoutWidget_2)
        self.label_denominator.setObjectName("label_denominator")
        self.horizontalLayout_denominator.addWidget(self.label_denominator)
        self.lineEdit_denominator = QtWidgets.QLineEdit(self.layoutWidget_2)
        self.lineEdit_denominator.setObjectName("lineEdit_denominator")
        self.horizontalLayout_denominator.addWidget(self.lineEdit_denominator)
        self.pushButton_add_theor_link = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_add_theor_link.setGeometry(QtCore.QRect(140, 230, 221, 51))
        self.pushButton_add_theor_link.setObjectName("pushButton_add_theor_link")
        self.label_theor_link_view = QtWidgets.QLabel(self.centralwidget)
        self.label_theor_link_view.setGeometry(QtCore.QRect(40, 180, 411, 41))
        self.label_theor_link_view.setObjectName("label_theor_link_view")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(40, 30, 411, 51))
        self.widget.setObjectName("widget")
        self.horizontalLayout_name_theor_link = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_name_theor_link.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_name_theor_link.setObjectName("horizontalLayout_name_theor_link")
        self.label_name_theor_link = QtWidgets.QLabel(self.widget)
        self.label_name_theor_link.setObjectName("label_name_theor_link")
        self.horizontalLayout_name_theor_link.addWidget(self.label_name_theor_link)
        self.lineEdit_name_theor_link = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_name_theor_link.setObjectName("lineEdit_name_theor_link")
        self.horizontalLayout_name_theor_link.addWidget(self.lineEdit_name_theor_link)
        MainWindow_theor_link_adding.setCentralWidget(self.centralwidget)
        self.add_functions()
        self.retranslateUi(MainWindow_theor_link_adding)
        QtCore.QMetaObject.connectSlotsByName(MainWindow_theor_link_adding)
        self.parent_ui = parent

    def add_functions(self):
        self.lineEdit_numerator.textEdited.connect(lambda: self.change_view_link())
        self.lineEdit_denominator.textEdited.connect(lambda: self.change_view_link())
        self.pushButton_add_theor_link.clicked.connect(lambda: self.add_theor_link_function_1(self.parent_ui))

    def change_view_link(self):
        _translate = QtCore.QCoreApplication.translate
        my_string = self.generate_string()
        if not (my_string is None):
            self.label_theor_link_view.setText(_translate("MainWindow_theor_link_adding",
                                                          "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">{}</span></p></body></html>".format(
                                                              my_string)))

    def add_theor_link_function_1(self, parent_1=None):
        try:
            parent_1.add_theor_link_function()
        except Exception:
            pass

    def generate_string(self):
        try:
            numerator_list = self.lineEdit_numerator.text().split()
            denominator_list = self.lineEdit_denominator.text().split()
            # Проверка на возможность перевести всё во float
            if len(numerator_list) * len(denominator_list) == 0:
                raise Exception
            for num in numerator_list:
                float(num)
            for num in denominator_list:
                float(num)
            num_str = "("
            for i in range(len(numerator_list)):
                if i != len(numerator_list) - 1:
                    num_str += str(numerator_list[i]) + "*s^" + str(len(numerator_list) - i - 1) + " + "
                else:
                    num_str += str(numerator_list[i])
            denom_str = ")/("
            for i in range(len(denominator_list)):
                if i != len(denominator_list) - 1:
                    denom_str += str(denominator_list[i]) + "*s^" + str(len(denominator_list) - i - 1) + " + "
                else:
                    denom_str += str(denominator_list[i]) + ")"
            return (num_str + denom_str)
        except Exception:
            return None

    def retranslateUi(self, MainWindow_theor_link_adding):
        _translate = QtCore.QCoreApplication.translate
        MainWindow_theor_link_adding.setWindowTitle(
            _translate("MainWindow_theor_link_adding", "Добавление теоретического звена"))
        self.label_numerator.setText(_translate("MainWindow_theor_link_adding",
                                                "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">Числитель звена</span></p></body></html>"))
        self.lineEdit_numerator.setText(_translate("MainWindow_theor_link_adding", "2 1"))
        self.label_denominator.setText(_translate("MainWindow_theor_link_adding",
                                                  "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">Знаменатель звена</span></p></body></html>"))
        self.lineEdit_denominator.setText(_translate("MainWindow_theor_link_adding", "1 2 1"))
        self.pushButton_add_theor_link.setText(_translate("MainWindow_theor_link_adding", "Добавить звено"))
        self.label_theor_link_view.setText(_translate("MainWindow_theor_link_adding",
                                                      "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">(2s + 1) / (s^2 + 2s + 1)</span></p></body></html>"))
        self.label_name_theor_link.setText(_translate("MainWindow_theor_link_adding",
                                                      "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">Название звена</span></p></body></html>"))
        self.lineEdit_name_theor_link.setText(
            _translate("MainWindow_theor_link_adding", "Новое теоретически заданное звено"))