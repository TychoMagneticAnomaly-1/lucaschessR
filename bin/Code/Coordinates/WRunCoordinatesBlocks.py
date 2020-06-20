import time

from PySide2 import QtCore, QtWidgets

import Code
from Code import Position
from Code.QT import Colocacion, Controles, Iconos, QTUtil, QTVarios, Tablero, QTUtil2


class WRunCoordinatesBlocks(QTVarios.WDialogo):
    def __init__(self, owner, db_coordinates, coordinates):

        QTVarios.WDialogo.__init__(self, owner, _("Coordinates by blocks"), Iconos.Blocks(), "runcoordinatesblocks")

        self.configuracion = Code.configuracion
        self.coordinates = coordinates
        self.db_coordinates = db_coordinates
        self.current_score = 0
        self.working = False
        self.time_ini = None

        conf_board = self.configuracion.config_board("RUNCOORDINATESBLOCKS", self.configuracion.size_base())

        self.board = Tablero.TableroEstaticoMensaje(self, conf_board, None, 0.6)
        self.board.crea()
        self.board.bloqueaRotacion(True)
        self.cp_initial = Position.Position()
        self.cp_initial.set_pos_initial()

        font = Controles.TipoLetra(puntos=self.configuracion.x_sizefont_infolabels)

        lb_block_k = Controles.LB(self, _("Block") + ":").ponFuente(font)
        self.lb_block = Controles.LB(self).ponFuente(font)

        lb_try_k = Controles.LB(self, _("Tries in this block") + ":").ponFuente(font)
        self.lb_try = Controles.LB(self).ponFuente(font)

        lb_minimum_score_k = Controles.LB(self, _("Minimum score") + ":").ponFuente(font)
        self.lb_minimum_score = Controles.LB(self).ponFuente(font)

        lb_current_score_block_k = Controles.LB(self, _("Max score in block") + ":").ponFuente(font)
        self.lb_current_score_block = Controles.LB(self).ponFuente(font)
        self.lb_current_score_enough = Controles.LB(self).ponImagen(Iconos.pmCorrecto())
        self.lb_current_score_enough.hide()

        self.lb_active_score_k = Controles.LB(self, _("Active score") + ":").ponFuente(font)
        self.lb_active_score = Controles.LB(self).ponFuente(font)

        li_acciones = ((_("Close"), Iconos.MainMenu(), self.terminar), None, (_("Begin"), Iconos.Empezar(), self.begin), (_("Continue"), Iconos.Pelicula_Seguir(), self.seguir))
        self.tb = QTVarios.LCTB(self, li_acciones)
        self.show_tb(self.terminar, self.begin)

        separacion = 20
        ly_info = Colocacion.G()
        ly_info.controld(lb_block_k, 0, 0).controld(self.lb_block, 0, 1)
        ly_info.filaVacia(1, separacion)
        ly_info.controld(lb_try_k, 2, 0).controld(self.lb_try, 2, 1)
        ly_info.filaVacia(3, separacion)
        ly_info.controld(lb_minimum_score_k, 4, 0).controld(self.lb_minimum_score, 4, 1)
        ly_info.filaVacia(5, separacion)
        ly_info.controld(lb_current_score_block_k, 6, 0).controld(self.lb_current_score_block, 6, 1)
        ly_info.filaVacia(7, separacion)
        ly_info.controld(self.lb_active_score_k, 8, 0).controld(self.lb_active_score, 8, 1)

        ly_right = Colocacion.V().control(self.tb).relleno().otro(ly_info).relleno()

        w = QtWidgets.QWidget(self)
        w.setLayout(ly_right)
        w.setMinimumWidth(240)

        ly_center = Colocacion.H().control(self.board).control(w).margen(3)

        self.setLayout(ly_center)

        self.restore_video()
        self.show_data()
        self.adjustSize()

    def new_try(self):
        is_white = self.coordinates.new_try()
        self.board.ponerPiezasAbajo(is_white)
        self.board.ponPosicion(self.cp_initial)
        self.lb_active_score_k.ponTexto(_("Active score") + ":")
        self.current_score = 0
        self.working = True
        self.time_ini = time.time()
        QtCore.QTimer.singleShot(1000, self.comprueba_time)

    def show_data(self):
        self.lb_block.ponTexto("%d/%d" % (self.coordinates.current_block + 1, self.coordinates.num_blocks()))
        self.lb_try.ponTexto("%d" % self.coordinates.current_try_in_block)
        self.lb_minimum_score.ponTexto("%d" % self.coordinates.min_score)
        self.lb_current_score_block.ponTexto("%d" % self.coordinates.current_max_in_block)

    def end_block(self):
        self.working = False
        self.board.pon_textos("", "", 1)
        self.lb_active_score_k.ponTexto(_("Last score") + ":")
        si_pasa_block, si_final = self.coordinates.new_done(self.current_score)
        self.db_coordinates.save(self.coordinates)
        if si_final:
            QTUtil2.message(self, "%s\n\n%s: %d\n" % (_("Ended"), _("Result"), self.coordinates.min_score))
            self.terminar()
            return
        else:
            if si_pasa_block:
                QTUtil2.message(self, _("Block ended"))
                self.lb_active_score.ponTexto("")
            self.show_tb(self.terminar, self.seguir)
        self.show_data()

    def comprueba_time(self):
        if self.working:
            dif_time = time.time() - self.time_ini
            if dif_time >= 30.0:
                self.end_block()
            else:
                tm = 1000 if dif_time > 1.0 else dif_time * 1000
                QtCore.QTimer.singleShot(tm, self.comprueba_time)

    def begin(self):
        self.seguir()

    def seguir(self):
        self.new_try()
        self.show_tb(self.terminar)
        self.lb_active_score.ponTexto("0")
        self.go_next()

    def go_next(self):
        if self.working:
            self.square_object, self.square_next = self.coordinates.next()
            self.board.pon_textos(self.square_object, self.square_next, 0.8)
            QTUtil.refresh_gui()

    def pulsada_celda(self, celda):
        if celda == self.square_object and self.working:
            self.current_score += 1
            self.lb_active_score.ponTexto("%d" % self.current_score)
            self.go_next()

    def closeEvent(self, event):
        self.working = False
        self.save_video()
        event.accept()

    def terminar(self):
        self.working = False
        self.save_video()
        self.reject()

    def show_tb(self, *lista):
        for opc in self.tb.dicTB:
            self.tb.setAccionVisible(opc, opc in lista)
        QTUtil.refresh_gui()