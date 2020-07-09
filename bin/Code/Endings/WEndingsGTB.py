import random
import time
import FasterCode

from PySide2 import QtWidgets, QtCore

from Code import Game
from Code import Move
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Columnas
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTVarios
from Code.QT import Tablero
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import Voyager
from Code.QT import FormLayout
from Code.Databases import DBgames
from Code.Endings import EndingsGTB
from Code.Endings import LibChess


PLAY_STOP, PLAY_NEXT_SOLVED, PLAY_NEXT_BESTMOVES = range(3)


class WEndingsGTB(QTVarios.WDialogo):
    def __init__(self, procesador):
        self.procesador = procesador
        self.configuracion = procesador.configuracion
        self.db = EndingsGTB.DBendings(self.configuracion)
        self.t4 = LibChess.T4(self.configuracion)

        QTVarios.WDialogo.__init__(
            self, procesador.main_window, _("Endings with Gaviota Tablebases"), Iconos.Finales(), "endings_gtb"
        )

        self.game = Game.Game()
        self.act_recno = -1

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Config"), Iconos.Configurar(), self.configurar),
            None,
            (_("Utilities"), Iconos.Utilidades(), self.utilidades),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        ly_bt, self.bt_movs = QTVarios.lyBotonesMovimiento(
            self, "", siTiempo=True, siLibre=False, rutina=self.run_botones, tamIcon=24
        )

        self.chb_help = Controles.CHB(self, _("Help mode"), False)
        ly_bt.espacio(20).control(self.chb_help)

        self.wpzs = QtWidgets.QWidget(self)
        self.wpzs.li_labels = []
        ly_wpzs = Colocacion.H()
        for x in range(6):
            lbl = Controles.LB(self.wpzs)
            self.wpzs.li_labels.append(lbl)
            ly_wpzs.control(lbl)
        self.wpzs.setLayout(ly_wpzs)
        self.wpzs.mousePressEvent = self.change

        self.color_done = QTUtil.qtColorRGB(213, 233, 250)

        li_acciones = (
            None,
            (" " + _("Play"), Iconos.Play1(), self.play),
            None,
            (" " + _("New"), Iconos.New1(), self.nuevo),
            None,
            (" " + _("Remove"), Iconos.Remove1(), self.remove),
            None,
        )
        self.tb_run = Controles.TBrutina(self, li_acciones, tamIcon=32, puntos=self.configuracion.x_tb_fontpoints)

        ly_top = Colocacion.H().control(tb).relleno().control(self.wpzs).relleno().control(self.tb_run)
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUM", _("N."), 50, centered=True)
        o_columns.nueva("XFEN", _("Position"), 140, centered=True)
        o_columns.nueva("MATE", _("Mate"), 60, centered=True)
        o_columns.nueva("TRIES", _("Tries"), 50, centered=True)
        o_columns.nueva("MOVES", _("Minimum moves"), 120, centered=True)
        o_columns.nueva("TIMEMS", _("Minimum time"), 120, centered=True)
        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True)
        self.grid.tipoLetra(puntos=self.configuracion.x_pgn_fontpoints)
        self.grid.ponAltoFila(self.configuracion.x_pgn_rowheight)
        self.grid.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        ly_pos = Colocacion.V().control(self.grid)

        config_board = self.configuracion.config_board("ENDINGSGTB", 64)
        self.tablero = TableroEndings(self, config_board)
        self.tablero.set_startup_control(self.startup_control)
        self.tablero.crea()
        self.tablero.ponerPiezasAbajo(True)
        self.tablero.set_dispatcher(self.mueve_humano)

        self.pzs = self.tablero.piezas
        self.playing = False

        ly_left_bottom = Colocacion.V().control(self.tablero).otro(ly_bt).relleno().margen(0)
        w = QtWidgets.QWidget(self)
        w.setLayout(ly_left_bottom)
        w.setFixedWidth(self.tablero.ancho + 16)

        ly_bottom = Colocacion.H().control(w).otro(ly_pos)

        layout = Colocacion.V().otro(ly_top).otro(ly_bottom).margen(6)
        self.setLayout(layout)

        self.restore_video()

        dic = self.configuracion.leeVariables("endingsGTB")

        self.key = key = dic.get("KEY")
        if (not key) or len(key) > self.configuracion.piezas_gaviota():
            key = "KPk"
        self.db.set_examples_auto(dic.get("EXAMPLES_AUTO", True))
        self.set_key(key)

        self.play_next_type = dic.get("PLAY_NEXT", PLAY_STOP)

        self.grid.gotop()
        self.play()

    def startup_control(self):
        if self.playing:
            if self.timer is None:
                self.timer = time.time()

    def reset(self):
        fila = self.grid.recno()
        self.act_recno = fila
        self.fen = self.db.get_current_fen(fila)
        self.game.set_fen(self.fen)
        self.tablero.setposition(self.game.first_position)
        self.bt_movs.hide()
        self.replaying = False
        self.grid.setFocus()

    def nuevo(self):
        self.reset()
        position = Voyager.voyager_position(self, self.game.first_position)
        if position is not None:
            fen = position.fen()
            mt = self.t4.dtm(fen)
            if mt is None:
                QTUtil2.message_error(self, _("Invalid, this position is not evaluated by Gaviota Tablebases"))
                return
            if mt < 0:
                QTUtil2.message_error(self, _("Invalid, this position is lost"))
                return
            key, fenm2 = self.db.insert(fen, mt)
            self.set_key(key)
            pos = self.db.pos_fen(fenm2)
            self.grid.goto(pos, 0)

    def play(self):
        fila = self.grid.recno()
        if fila < 0:
            return

        if len(self.game) > 0 and not self.game.is_finished():
            self.db.register_empty_try(fila)
            self.grid.refresh()

        if (
            self.t4.dtm(self.game.first_position.fen()) is None
        ):  # En el caso de que se desinstale g5 y se trate de resolver un 5pzs
            QTUtil2.message_error(self, _("Invalid, this position is not evaluated by Gaviota Tablebases"))
            return

        self.game.reset()
        self.tablero.setposition(self.game.first_position)
        self.test_help()
        self.bt_movs.hide()
        self.ms = 0
        self.moves = 0
        self.is_helped = False
        self.replaying = False
        self.timer = None
        self.playing = True
        self.sigueHumano()

    def play_next(self):
        fila = self.grid.recno()
        if 0 <= fila < (self.db.current_num_fens() - 1):
            self.grid.goto(fila + 1, 0)
            self.play()

    def remove(self):
        fila = self.grid.recno()
        if fila >= 0:
            if QTUtil2.pregunta(self, "Do you want to remove this position?"):
                self.db.remove(fila)
                self.grid.refresh()
                self.grid_cambiado_registro(None, fila, None)

    def configurar(self):
        dic_vars = self.configuracion.leeVariables("endingsGTB")

        form = FormLayout.FormLayout(self, _("Configuration"), Iconos.Finales())
        form.separador()

        li_options = ((_("Initial"), "initial"), (_("By difficulty"), "difficulty"), (_("Random"), "random"))
        order = dic_vars.get("ORDER", "initial")
        form.combobox(_("Order of positions"), li_options, order)
        form.separador()

        li_options = (
            (_("Stop"), PLAY_STOP),
            (_("Jump to the next"), PLAY_NEXT_SOLVED),
            (_("Jump to the next if minimum moves done"), PLAY_NEXT_BESTMOVES),
        )
        play_next = dic_vars.get("PLAY_NEXT", PLAY_STOP)
        form.combobox(_("What to do after solving"), li_options, play_next)
        form.separador()

        examples = dic_vars.get("EXAMPLES_AUTO", True)
        form.checkbox(_("Import examples automatically"), examples)
        form.separador()

        resp = form.run()
        if resp:
            accion, liResp = resp
            order, play_next, examples_auto = liResp
            dic_vars["PLAY_NEXT"] = self.play_next_type = play_next
            dic_vars["ORDER"] = order
            dic_vars["EXAMPLES_AUTO"] = examples_auto
            self.db.examples_auto = examples_auto
            self.configuracion.escVariables("endingsGTB", dic_vars)

    def set_key(self, key):
        self.key = self.db.test_tipo(key)
        dic = self.configuracion.leeVariables("endingsGTB")
        order = dic.get("ORDER", "difficulty")
        dic["KEY"] = self.key
        self.configuracion.escVariables("endingsGTB", dic)
        num_positions = self.db.read_key(self.key, order)
        self.grid.refresh()

        pos = 0
        for c in key:
            lbl = self.wpzs.li_labels[pos]
            lbl.ponImagen(self.pzs.pixmap(c, 48))
            lbl.show()
            pos += 1
        while pos < 6:
            self.wpzs.li_labels[pos].hide()
            pos += 1

        self.bt_movs.hide()
        self.replaying = False
        self.grid.setFocus()

        if num_positions:
            self.act_recno = 0
            self.fen = self.db.get_current_fen(0)
            self.game.set_fen(self.fen)
        else:
            self.act_recno = -1
            self.game = Game.Game()

        self.tablero.setposition(self.game.first_position)

    def grid_num_datos(self, grid):
        return self.db.current_num_fens()

    def grid_dato(self, grid, fila, ocol):
        clave = ocol.clave
        if clave == "NUM":
            return str(fila + 1)
        else:
            data = self.db.current_fen_field(fila, ocol.clave, None)
            if data is None:
                return ""
            if clave == "MATE":
                tok = self.db.current_fen_field(fila, "TRIES_OK")
                tr = self.db.current_fen_field(fila, "TRIES")
                if data == 0:
                    return _("Draw")
                else:
                    return str((data + 1) // 2)
            elif clave == "TIMEMS":
                mt = self.db.current_fen_field(fila, "MATE")
                if mt == 0:
                    moves = self.db.current_fen_field(fila, "MOVES")
                else:
                    moves = (mt + 1) // 2
                factor = data / (moves * 1000)
                return "%.1f (%.1f)" % (data / 1000, factor)

            elif clave == "TRIES":
                tok = self.db.current_fen_field(fila, "TRIES_OK")
                return "%d/%d" % (data, tok)
            return str(data)

    def grid_cambiado_registro(self, grid, fila, columna):
        if fila >= 0:
            self.reset()
            self.play()

    def grid_bold(self, grid, fila, oColumna):
        return fila == self.act_recno

    def grid_color_fondo(self, grid, fila, oColumna):
        tok = self.db.current_fen_field(fila, "TRIES_OK")
        if tok > 0:
            mt = self.db.current_fen_field(fila, "MATE")
            if mt == 0 or ((mt + 1) // 2 == self.db.current_fen_field(fila, "MOVES")):
                return self.color_done

    def grid_doble_click(self, grid, fila, oColumna):
        self.play()

    def grid_boton_derecho(self, grid, fila, oColumna, modif):
        menu = QTVarios.LCMenu(self)
        menu.opcion("reset", _("Reset data to 0"), Iconos.Delete())
        resp = menu.lanza()
        if resp == "reset":
            self.db.reset_data_pos(fila)
            self.grid.refresh()

    def terminar(self):
        self.save_video()
        self.db.close()
        self.t4.close()
        self.procesador.pararMotores()
        self.accept()

    def closeEvent(self, event):
        self.db.close()
        self.t4.close()
        self.save_video()

    def change(self, event):
        rondo = QTVarios.rondoPuntos()
        menu = QTVarios.LCMenuPiezas(self)

        dsubmenus = {"Q": [], "R": [], "B": [], "N": [], "P": [], "k": []}
        for key in self.db.keylist(self.db.examples_auto, True):
            dsubmenus[key[1]].append(key)

        for key, li in dsubmenus.items():
            if li:
                submenu = menu.submenu("K" + key, rondo.otro())
                for keymenu in li:
                    submenu.opcion(keymenu, keymenu, rondo.otro())

        resp = menu.lanza()
        if resp:
            self.set_key(resp)
            self.tablero.activaColor(self.game.last_position.is_white)

    def sigueHumano(self):
        ended, go_next = self.test_final()
        if ended:
            if go_next:
                self.play_next()
            return
        self.tablero.activaColor(self.game.last_position.is_white)
        self.test_help()

    def test_final(self):
        if self.game.is_finished():
            self.tablero.disable_all()
            self.playing = False
            recno = self.grid.recno()
            ok, mensaje = self.db.register_try(recno, self.game, self.ms, self.moves, self.is_helped)
            go_next = False
            mate = self.db.current_fen_field(recno, "MATE")
            mt_white = (mate + 1) // 2
            if ok:
                if self.is_helped:
                    go_next = False
                else:
                    if self.play_next_type == PLAY_STOP:
                        go_next = False
                    elif self.play_next_type == PLAY_NEXT_SOLVED:
                        go_next = True
                    else:
                        go_next = self.moves == mt_white

                if self.grid_num_datos(None) == (self.grid.recno() + 1):
                    go_next = False

                if not go_next:
                    QTUtil2.message_accept(self, _("Done"), explanation=mensaje)
            else:
                QTUtil2.message_error(self, _("Failed attempt"))

            self.bt_movs.show()
            self.pos_game = len(self.game) - 1
            return True, go_next
        return False, None

    def sigueMaquina(self):
        ended, go_next = self.test_final()
        if ended:
            if go_next:
                self.play_next()
            return
        lista = self.t4.best_moves_game(self.game)
        if len(lista) == 0:
            return
        move = random.choice(lista)
        from_sq, to_sq, promotion = move[:2], move[2:4], move[4:]
        siBien, mens, move = Move.dameJugada(self.game, self.game.last_position, from_sq, to_sq, promotion)
        self.game.add_move(move)
        for movim in move.liMovs:
            if movim[0] == "b":
                self.tablero.borraPieza(movim[1])
            elif movim[0] == "m":
                self.tablero.muevePieza(movim[1], movim[2])
            elif movim[0] == "c":
                self.tablero.cambiaPieza(movim[1], movim[2])
        self.timer = time.time()
        self.sigueHumano()

    def mueve_humano(self, from_sq, to_sq, promotion=None):
        if self.timer:
            self.ms += int((time.time() - self.timer) * 1000)
        self.moves += 1
        self.timer = None

        movimiento = from_sq + to_sq

        # Peon coronando
        if not promotion and self.game.last_position.siPeonCoronando(from_sq, to_sq):
            promotion = self.tablero.peonCoronando(self.game.last_position.is_white)
            if promotion is None:
                self.sigueHumano()
                return False
        if promotion:
            movimiento += promotion

        ok, self.error, move = Move.dameJugada(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if ok:
            self.game.add_move(move)
            self.tablero.setposition(move.position)
            self.sigueMaquina()
            return True
        else:
            return False

    def test_help(self):
        if not self.chb_help.valor():
            return
        self.is_helped = True
        fen = self.game.last_position.fen()
        lif = [x[:2] for x in self.t4.best_mvs(fen)]
        if lif:
            self.tablero.ponFlechaSCvar(lif, opacidad=1.0)

    def pon_position(self):
        if self.pos_game == -1:
            position = self.game.first_position
        elif self.pos_game >= len(self.game):
            position = self.game.last_position
        else:
            move = self.game.move(self.pos_game)
            position = move.position
        self.tablero.setposition(position)

        lif = [x[:2] for x in self.t4.best_mvs(position.fen())]
        if lif:
            self.tablero.ponFlechaSCvar(lif, opacidad=1.0)
            if (self.pos_game + 1) < len(self.game):
                move = self.game.move(self.pos_game + 1)
                ok = True
                for desde, hasta in lif:
                    if desde == move.from_sq and hasta[:2] == move.to_sq:
                        ok = False
                        break
                if ok:
                    self.tablero.ponFlechaSC(move.from_sq, move.to_sq)

    def mover_tiempo(self):
        if not self.replaying:
            return
        self.pos_game += 1
        if self.pos_game == len(self.game):
            return
        self.pon_position()
        QtCore.QTimer.singleShot(self.configuracion.x_interval_replay, self.mover_tiempo)

    def run_botones(self):
        key = self.sender().clave
        if key == "MoverTiempo":
            if self.replaying:
                self.replaying = False
            else:
                self.replaying = True
                self.pos_game = -1
                self.pon_position()
                QtCore.QTimer.singleShot(self.configuracion.x_interval_replay, self.mover_tiempo)
            return
        elif key == "MoverInicio":
            self.pos_game = -1
        elif key == "MoverAtras":
            if 0 <= self.pos_game:
                self.pos_game -= 1
        elif key == "MoverAdelante":
            if self.pos_game < len(self.game):
                self.pos_game += 1
        elif key == "MoverFinal":
            self.pos_game = len(self.game) - 1
        self.pon_position()

    def utilidades(self):
        menu = QTVarios.LCMenu(self)

        submenu = menu.submenu(_("Import"), Iconos.Import8())
        submenu.opcion("examples", _("Examples"), Iconos.Gafas())
        submenu.separador()
        submenu.opcion("pgn", _("PGN"), Iconos.Tablero())
        submenu.separador()
        submenu.opcion("database", _("Database"), Iconos.Database())
        submenu.separador()
        submenu.opcion("fns", _("Text file"), Iconos.Fichero())

        menu.separador()

        submenu = menu.submenu(_("Remove"), Iconos.Delete())
        submenusubmenu1 = submenu.submenu(_("Positions"), Iconos.TrainPositions())
        submenusubmenu1.opcion("remp_all", _("Remove all positions"), Iconos.PuntoRojo())
        submenusubmenu1.opcion("remp_all_group", _("Remove all positions of current group"), Iconos.PuntoRojo())
        submenu.separador()
        submenusubmenu2 = submenu.submenu(_("Results"), Iconos.Reciclar())
        submenusubmenu2.opcion("remr_all", _("Remove results of all positions"), Iconos.PuntoNaranja())
        submenusubmenu2.opcion(
            "remr_all_group", _("Remove results of all positions of current group"), Iconos.PuntoNaranja()
        )
        menu.separador()
        resp = menu.lanza()
        if resp is None:
            return
        if resp == "pgn":
            self.import_pgn()
        elif resp == "database":
            self.import_db()
        elif resp == "examples":
            self.import_examples()
        elif resp == "fns":
            self.import_fns()
        elif resp.startswith("remr"):
            self.remove_all_results(resp[9:])
        elif resp.startswith("remp"):
            self.remove_all_positions(resp[9:])

    def import_lifens(self, tipo, lifens, um):
        li = []
        for fen in lifens:
            mt = self.t4.dtm(fen)
            if mt and mt >= 0:
                li.append((fen, mt))
        if li:
            self.db.import_lista(tipo, li)
        um.final()

        self.mensaje_import(len(li))
        self.set_key(self.key)
        self.tablero.activaColor(self.game.last_position.is_white)

    def mensaje_import(self, num):
        if num:
            QTUtil2.message(self, "%s: %d %s" % (_("Imported"), num, _("positions")))
        else:
            QTUtil2.message_error(self, _("Nothing to import"))

    def import_pgn(self):
        li_path_pgn = QTVarios.select_pgns(self)
        if not li_path_pgn:
            return
        um = QTUtil2.unMomento(self, _("Working..."))
        li_fens = []
        for path_pgn in li_path_pgn:
            with FasterCode.PGNreader(path_pgn, 1) as fpgn:
                for (body, raw, pv, liFens, bdCab, bdCablwr, btell) in fpgn:
                    if b"FEN" in bdCab:
                        fen = bdCab[b"FEN"].decode()
                        li_fens.append(fen)
        self.import_lifens("pgn", li_fens, um)

    def import_db(self):
        path_db = QTVarios.select_db(self, self.configuracion, True, False)
        if not path_db:
            return
        um = QTUtil2.unMomento(self, _("Working..."))
        li_fens = []
        datadb = DBgames.DBgames(path_db)
        if "FEN" in datadb.li_tags():
            for reg in datadb.yieldData(["FEN"], "FEN <> ''"):
                li_fens.append(reg.FEN)
        self.import_lifens("db", li_fens, um)

    def import_examples(self):
        rondo = QTVarios.rondoPuntos()
        menu = QTVarios.LCMenuPiezas(self)

        dsubmenus = {"Q": [], "R": [], "B": [], "N": [], "P": [], "k": []}
        for key in self.db.keylist(examples=True, own=False):
            dsubmenus[key[1]].append(key)

        for key, li in dsubmenus.items():
            if li:
                submenu = menu.submenu("K" + key, rondo.otro())
                for keymenu in li:
                    submenu.opcion(keymenu, keymenu, rondo.otro())

        key = menu.lanza()
        if key:
            num = self.db.add_examples(key)
            self.key = key
            self.mensaje_import(num)
            self.set_key(self.key)
            self.tablero.activaColor(self.game.last_position.is_white)

    def import_fns(self):
        path_fich = QTUtil2.leeFichero(self, "", "*")
        if path_fich:
            um = QTUtil2.unMomento(self, _("Working..."))
            li_fens = []
            with open(path_fich, "rt") as f:
                for linea in f:
                    li = linea.strip().split(" ")
                    if li and len(li) >= 2:
                        if li[1] in "wb":
                            fen = "%s %s - -" % (li[0], li[1])
                            li_fens.append(fen)
            self.import_lifens("fns", li_fens, um)

    def remove_all_results(self, mas):
        self.db.remove_results(mas == "group")
        self.set_key(self.key)

    def remove_all_positions(self, mas):
        self.db.remove_positions(mas == "group")
        self.set_key(self.key)


def train_gtb(procesador):
    w = WEndingsGTB(procesador)
    w.exec_()


class TableroEndings(Tablero.Tablero):
    def set_startup_control(self, startup_control):
        self.startup_control = startup_control

    def mousePressEvent(self, event):
        self.startup_control()
        Tablero.Tablero.mousePressEvent(self, event)
