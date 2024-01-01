import sys
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from conexion_sqlite import Comunicacion
from PyQt5 import uic
import os

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super(VentanaPrincipal, self).__init__()
        loadUi('diseño.ui', self)

        ruta_diseño_ui = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'diseño.ui')

        uic.loadUi(ruta_diseño_ui, self)


        self.bt_menu.clicked.connect(self.mover_menu)
        #clase comunicacion sqlite
        self.base_de_datos = Comunicacion()


        #ocultamos los botones
        self.bt_restaurar.hide()
        #botones
        self.bt_refrescar.clicked.connect(self.mostrar_productos)
        self.bt_agregar.clicked.connect(self.registrar_productos)
        self.bt_borrar.clicked.connect(self.eliminar_productos)
        self.bt_actualiza_tabla.clicked.connect(self.modificar_productos)
        self.bt_actualiza_buscar.clicked.connect(self.buscar_por_nombre_actualiza) #si hay algún error verifica esta parte
        self.bt_buscar_borrar.clicked.connect(self.buscar_por_nombre_eliminar)

        #control barra de titulos
        self.bt_minimizar.clicked.connect(self.control_bt_minimizar)
        self.bt_restaurar.clicked.connect(self.control_bt_normal)
        self.bt_maximizar.clicked.connect(self.control_bt_maximizar)
        self.bt_cerrar.clicked.connect(lambda: self.close())

        #eliminar barra de titulo y opacidad
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)

        #sizegrip
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)

        #mover ventana
        self.frame_superior.mouseMoveEvent = self.mover_ventana

        #conexión botones
        self.bt_datos.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_datos))
        self.bt_registrar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_registrar))
        self.bt_actualizar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_actualizar))
        self.bt_eliminar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_eliminar))
        self.bt_ajustes.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_ajustes))
        
        #ancho de columna adaptable
        self.tabla_borrar.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #llamar automaticamente a mostrar los datos de la tabla
        self.mostrar_productos()


    def control_bt_minimizar(self):
        self.showMinimized()


    def control_bt_normal(self):
        self.showNormal()
        self.bt_maximizar.show()
        self.bt_restaurar.hide()

    def control_bt_maximizar(self):
        self.showMaximized()
        self.bt_maximizar.hide()
        self.bt_restaurar.show()
    
    ## sizegrip
    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)


    #mover ventana
    def mousePressEvent(self, event):
        self.click_position = event.globalPos()

    
    def mover_ventana(self, event):
        if self.isMaximized() == False:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.click_position)
                self.click_position= event.globalPos()
                event.accept()
            if event.globalPos().y() <= 10:
                self.showMaximized()
                self.bt_maximizar.hide()
                self.bt_restaurar.show()
            else:
                self.showNormal()
                self.bt_restaurar.hide()
                self.bt_maximizar.show()

            
    
    #metodo para mover rel menu lateal izquierdo
    def mover_menu(self):
        if True:
            width = self.frame_control.width()
            normal = 0
            if width == 0:
                extender = 200
            else:
                extender = normal
            self.animacion = QPropertyAnimation(self.frame_control, b'minimumWidth')
            self.animacion.setDuration(300)
            self.animacion.setStartValue(width)
            self.animacion.setEndValue(extender)
            self.animacion.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animacion.start()

        
    #configuracion página base de datos
    def mostrar_productos(self):
        datos = self.base_de_datos.mostrar_productos()
        i = len(datos)
        self.tabla_productos.setRowCount(i)
        tablerow = 0
        for row in datos:
            self.Id= row[0]
            self.tabla_productos.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(row[1])))
            self.tabla_productos.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(str(row[2])))
            self.tabla_productos.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(str(row[3])))
            self.tabla_productos.setItem(tablerow, 3, QtWidgets.QTableWidgetItem(str(row[4])))
            self.tabla_productos.setItem(tablerow, 4, QtWidgets.QTableWidgetItem(str(row[5])))
            tablerow += 1
            self.signal_actualizar.setText("")
            self.signal_registrar.setText("")
            self.signal_eliminacion.setText("")



    def registrar_productos(self):
        codigo = self.reg_codigo.text().upper()
        nombre = self.reg_nombre.text().upper()
        modelo = self.reg_modelo.text().upper()
        precio = self.reg_precio.text().upper()
        cantidad = self.reg_cantidad.text().upper()
        if codigo != '' and nombre != '' and modelo != '' and precio != '' and cantidad != '':
            self.base_de_datos.inserta_producto(codigo, nombre, modelo, precio, cantidad)
            self.signal_registrar.setText('Productos Registrados')
            self.reg_codigo.clear()
            self.reg_nombre.clear()
            self.reg_modelo.clear()
            self.reg_precio.clear()
            self.reg_cantidad.clear()
        else:
            self.signal_registrar.setText('Hay espacios vacíos')
        

    def buscar_por_nombre_actualiza(self):
        id_producto = self.act_buscar.text().upper()
        id_producto = str("'" + id_producto + "'")
        self.producto = self.base_de_datos.busca_producto(id_producto)
        if len(self.producto) !=0:
            self.Id = self.producto[0][0]
            self.act_codigo.setText(str(self.producto[0][1]))
            self.act_nombre.setText(str(self.producto[0][2]))
            self.act_modelo.setText(str(self.producto[0][3]))
            self.act_precio.setText(str(self.producto[0][4]))
            self.act_cantidad.setText(str(self.producto[0][5]))
        else:
            self.signal_actualizar.setText("NO EXISTE")

        
    def modificar_productos(self):
        if self.producto != '':
            codigo = self.act_codigo.text().upper()
            nombre = self.act_nombre.text().upper()
            modelo = self.act_modelo.text().upper()
            precio = self.act_precio.text().upper()
            cantidad = self.act_cantidad.text().upper()
            act = self.base_de_datos.actualiza_productos(self.Id, codigo, nombre, modelo, precio, cantidad)
            if act == 1:
                self.signal_actualizar.setText("ACTUALIZADO")
                self.act_codigo.clear()
                self.act_nombre.clear()
                self.act_modelo.clear()
                self.act_precio.clear()
                self.act_cantidad.clear()
                self.act_buscar.setText('')
            elif act == 0:
                self.signal_actualizar.setText("ERROR")
            else:
                self.signal_actualizar.setText("INCORRECTO")


    def buscar_por_nombre_eliminar(self):
        nombre_producto = self.eliminar_buscar.text().upper()
        nombre_producto = str("'" + nombre_producto + "'")
        producto = self.base_de_datos.busca_producto(nombre_producto)
        self.tabla_borrar.setRowCount(len(producto))

        if len(producto) == 0:
            self.signal_eliminacion.setText(' No existe')
        else:
            self.signal_eliminacion.setText('Producto Seleccionado')
        tablerow = 0
        for row in producto:
            self.producto_a_borrar = row[2]
            self.tabla_borrar.setItem(tablerow,0,QtWidgets.QTableWidgetItem(row[1]))
            self.tabla_borrar.setItem(tablerow,1,QtWidgets.QTableWidgetItem(row[2]))
            self.tabla_borrar.setItem(tablerow,2,QtWidgets.QTableWidgetItem(row[3]))
            self.tabla_borrar.setItem(tablerow,3,QtWidgets.QTableWidgetItem(str(row[4])))
            self.tabla_borrar.setItem(tablerow,4,QtWidgets.QTableWidgetItem(str(row[5])))
            tablerow += 1

        
    def eliminar_productos(self):
        self.row_flag = self.tabla_borrar.currentRow()
        if self.row_flag == 0:
            self.tabla_borrar.removeRow(0)
            self.base_de_datos.elimina_productos("'" + self.producto_a_borrar +"'")
            self.signal_eliminacion.setText('Producto Eliminado')
            self.eliminar_buscar.setText('')

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mi_app = VentanaPrincipal()
    mi_app.show()
    sys.exit(app.exec_())