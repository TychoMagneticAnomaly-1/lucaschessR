import os

import FasterCode

from PySide2 import QtWidgets, QtCore

from Code.Polyglots import Books
from Code.Base import Game, Position
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTVarios
from Code.QT import Columnas
from Code.QT import Grid
from Code.QT import QTUtil2
from Code.QT import Delegados
from Code.Databases import WDB_Summary, DBgamesST


class TabEngine(QtWidgets.QWidget):
    def __init__(self, tabsAnalisis, procesador, configuration):
        QtWidgets.QWidget.__init__(self)

        self.analyzing = False
        self.position = None
        self.li_analysis = []
        self.manager_motor = None
        self.current_mrm = None

        self.dbop = tabsAnalisis.dbop

        self.procesador = procesador
        self.configuration = configuration
        self.with_figurines = configuration.x_pgn_withfigurines

        self.tabsAnalisis = tabsAnalisis
        self.bt_start = Controles.PB(self, "", self.start).ponIcono(Iconos.Pelicula_Seguir(), 32)
        self.bt_stop = Controles.PB(self, "", self.stop).ponIcono(Iconos.Pelicula_Pausa(), 32)
        self.bt_stop.hide()

        self.lb_engine = Controles.LB(self, _("Engine") + ":")
        liMotores = configuration.comboMotores()  # (name, key)
        default = configuration.tutor.key
        engine = self.dbop.getconfig("ENGINE", default)
        if len([key for name, key in liMotores if key == engine]) == 0:
            engine = default
        self.cb_engine = Controles.CB(self, liMotores, engine).capture_changes(self.reset_motor)

        multipv = self.dbop.getconfig("ENGINE_MULTIPV", 5)
        lb_multipv = Controles.LB(self, _("Multi PV") + ": ")
        self.sb_multipv = Controles.SB(self, multipv, 1, 500).tamMaximo(50)

        self.lb_analisis = (
            Controles.LB(self, "").set_background("#C9D2D7").ponTipoLetra(puntos=configuration.x_pgn_fontpoints)
        )

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("PDT", _("Evaluation"), 120, centered=True)
        delegado = Delegados.EtiquetaPOS(True, siLineas=False) if self.with_figurines else None
        o_columns.nueva("SOL", "", 100, centered=True, edicion=delegado)
        o_columns.nueva("PGN", _("Solution"), 860)

        self.grid_analysis = Grid.Grid(self, o_columns, siSelecFilas=True, siCabeceraVisible=False)
        self.grid_analysis.tipoLetra(puntos=configuration.x_pgn_fontpoints)
        self.grid_analysis.ponAltoFila(configuration.x_pgn_rowheight)
        # self.register_grid(self.grid_analysis)

        ly_lin1 = Colocacion.H().control(self.bt_start).control(self.bt_stop).control(self.lb_engine)
        ly_lin1.control(self.cb_engine)
        ly_lin1.espacio(50).control(lb_multipv).control(self.sb_multipv).relleno()
        ly = Colocacion.V().otro(ly_lin1).control(self.lb_analisis).control(self.grid_analysis).margen(3)

        self.setLayout(ly)

        self.reset_motor()

    def saveCurrent(self):
        if self.current_mrm:
            fenm2 = self.current_posicion.fenm2()
            dic = self.dbop.getfenvalue(fenm2)
            if "ANALISIS" in dic:
                mrm_ant = dic["ANALISIS"]
                if mrm_ant.getdepth0() > self.current_mrm.getdepth0():
                    return
            dic["ANALISIS"] = self.current_mrm
            self.dbop.setfenvalue(fenm2, dic)

    def setData(self, label, position):
        self.saveCurrent()
        self.position = position
        self.lb_analisis.set_text(label)
        if self.analyzing:
            self.analyzing = False
            self.manager_motor.ac_final(0)
            game = Game.Game(self.position)
            self.manager_motor.ac_inicio(game)
            self.analyzing = True
            QtCore.QTimer.singleShot(1000, self.lee_analisis)
        else:
            fenm2 = position.fenm2()
            dic = self.dbop.getfenvalue(fenm2)
            if "ANALISIS" in dic:
                self.show_analisis(dic["ANALISIS"])
            else:
                self.li_analysis = []
                self.grid_analysis.refresh()

    def start(self):
        self.current_mrm = None
        self.current_posicion = None
        self.sb_multipv.setDisabled(True)
        self.cb_engine.setDisabled(True)
        self.analyzing = True
        self.sb_multipv.setDisabled(True)
        self.show_stop()
        multipv = self.sb_multipv.valor()
        self.manager_motor.actMultiPV(multipv)
        game = Game.Game(self.position)
        self.manager_motor.ac_inicio(game)
        QtCore.QTimer.singleShot(1000, self.lee_analisis)

    def show_start(self):
        self.bt_stop.hide()
        self.bt_start.show()

    def show_stop(self):
        self.bt_start.hide()
        self.bt_stop.show()

    def show_analisis(self, mrm):
        self.current_mrm = mrm
        self.current_posicion = self.position
        li = []
        for rm in mrm.li_rm:
            game = Game.Game(self.position)
            game.read_pv(rm.pv)
            pgn = game.pgnBaseRAW()
            lit = pgn.split(" ")
            is_white = self.position.is_white
            if is_white:
                pgn0 = lit[0].split(".")[-1]
                pgn1 = " ".join(lit[1:])
            else:
                pgn0 = lit[1]
                pgn1 = " ".join(lit[2:])

            if self.with_figurines:
                game.ms_sol = pgn0, is_white, None, None, None, None, False, False
            else:
                game.ms_sol = pgn0
            game.ms_pgn = pgn1
            game.ms_pdt = rm.abrTextoPDT()
            li.append(game)
        self.li_analysis = li
        self.grid_analysis.refresh()

    def lee_analisis(self):
        if self.analyzing:
            mrm = self.manager_motor.ac_estado()
            self.show_analisis(mrm)
            QtCore.QTimer.singleShot(2000, self.lee_analisis)

    def stop(self):
        self.saveCurrent()
        self.sb_multipv.setDisabled(False)
        self.cb_engine.setDisabled(False)
        self.analyzing = False
        self.show_start()
        if self.manager_motor:
            self.manager_motor.ac_final(0)

    def reset_motor(self):
        self.saveCurrent()
        key = self.cb_engine.valor()
        if not key:
            return
        self.analyzing = False
        if self.manager_motor:
            self.manager_motor.terminar()
        self.stop()
        conf_engine = self.configuration.buscaRival(key)

        multipv = self.sb_multipv.valor()
        self.manager_motor = self.procesador.creaManagerMotor(conf_engine, 0, 0, siMultiPV=multipv > 1)

    def grid_num_datos(self, grid):
        return len(self.li_analysis)

    def grid_dato(self, grid, row, o_column):
        if o_column.key == "PDT":
            return self.li_analysis[row].ms_pdt
        elif o_column.key == "SOL":
            return self.li_analysis[row].ms_sol
        else:
            return self.li_analysis[row].ms_pgn

    def saveConfig(self):
        self.dbop.setconfig("ENGINE", self.cb_engine.valor())
        self.dbop.setconfig("ENGINE_MULTIPV", self.sb_multipv.valor())


class TabBook(QtWidgets.QWidget):
    def __init__(self, tabsAnalisis, book, configuration):
        QtWidgets.QWidget.__init__(self)

        self.tabsAnalisis = tabsAnalisis
        self.position = None
        self.leido = False

        self.book = book
        book.polyglot()
        self.li_moves = []

        self.with_figurines = configuration.x_pgn_withfigurines

        o_columns = Columnas.ListaColumnas()
        delegado = Delegados.EtiquetaPOS(True, siLineas=False) if self.with_figurines else None
        for x in range(20):
            o_columns.nueva(x, "", 80, centered=True, edicion=delegado)
        self.grid_moves = Grid.Grid(
            self, o_columns, siSelecFilas=True, siCabeceraMovible=False, siCabeceraVisible=False
        )
        self.grid_moves.tipoLetra(puntos=configuration.x_pgn_fontpoints)
        self.grid_moves.ponAltoFila(configuration.x_pgn_rowheight)

        ly = Colocacion.V().control(self.grid_moves).margen(3)

        self.setLayout(ly)

    def grid_num_datos(self, grid):
        return len(self.li_moves)

    def grid_dato(self, grid, row, o_column):
        mv = self.li_moves[row]
        li = mv.dato
        key = int(o_column.key)
        pgn = li[key]
        if self.with_figurines:
            is_white = " w " in mv.fen
            return pgn, is_white, None, None, None, None, False, True
        else:
            return pgn

    def grid_doble_click(self, grid, row, o_column):
        self.lee_subnivel(row)
        self.grid_moves.refresh()

    def grid_right_button(self, grid, row, column, modificadores):
        self.borra_subnivel(row)
        self.grid_moves.refresh()

    def setData(self, position):
        self.position = position
        self.start()

    def borra_subnivel(self, row):
        alm = self.li_moves[row]
        nv = alm.nivel
        if nv == 0:
            return
        li = []
        for x in range(row, 0, -1):
            alm1 = self.li_moves[x]
            if alm1.nivel < nv:
                break
            li.append(x)
        for x in range(row + 1, len(self.li_moves)):
            alm1 = self.li_moves[x]
            if alm1.nivel < nv:
                break
            li.append(x)
        li.sort(reverse=True)
        for x in li:
            del self.li_moves[x]

    def lee_subnivel(self, row):
        alm_base = self.li_moves[row]
        if alm_base.nivel >= 17:
            return
        FasterCode.set_fen(alm_base.fen)
        if FasterCode.move_pv(alm_base.from_sq, alm_base.to_sq, alm_base.promotion):
            fen = FasterCode.get_fen()
            for alm in self.book.almListaJugadas(fen):
                nv = alm.nivel = alm_base.nivel + 1
                alm.dato = [""] * 20
                alm.dato[nv] = alm.pgn
                alm.dato[nv + 1] = alm.porc
                alm.dato[nv + 2] = "%d" % alm.weight
                row += 1
                self.li_moves.insert(row, alm)

    def lee(self):
        if not self.leido and self.position:
            fen = self.position.fen()
            self.li_moves = self.book.almListaJugadas(fen)
            for alm in self.li_moves:
                alm.nivel = 0
                alm.dato = [""] * 20
                alm.dato[0] = alm.pgn
                alm.dato[1] = alm.porc
                alm.dato[2] = "%d" % alm.weight
            self.leido = True

    def start(self):
        self.leido = False
        self.lee()
        self.grid_moves.refresh()

    def stop(self):
        pass


class TabDatabase(QtWidgets.QWidget):
    def __init__(self, tabsAnalisis, procesador, dbstat):
        QtWidgets.QWidget.__init__(self)

        self.tabsAnalisis = tabsAnalisis

        self.pv = None

        self.dbstat = dbstat

        self.wsummary = WDB_Summary.WSummaryBase(procesador, dbstat)

        layout = Colocacion.H().control(self.wsummary)
        self.setLayout(layout)

    def setData(self, pv):
        self.pv = pv
        self.wsummary.actualizaPV(self.pv)

    def start(self):
        self.wsummary.actualizaPV(self.pv)

    def stop(self):
        self.dbstat.close()


class TreeMoves(QtWidgets.QTreeWidget):
    def __init__(self, owner):
        QtWidgets.QTreeWidget.__init__(self, owner)
        self.owner = owner

    def mousePressEvent(self, event):
        QtWidgets.QTreeWidget.mousePressEvent(self, event)
        self.resizeColumnToContents(0)
        self.owner.seleccionado()


class TabTree(QtWidgets.QWidget):
    def __init__(self, tabsAnalisis, configuration):
        QtWidgets.QWidget.__init__(self)

        self.tabsAnalisis = tabsAnalisis

        self.tree = TreeMoves(self)

        self.tree.setAlternatingRowColors(True)

        self.tree.setIndentation(24)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.menuContexto)
        self.tree.setStyleSheet("selection-background-color: #F1D369; selection-color: #000000;")
        self.tree.setFont(Controles.TipoLetra(puntos=configuration.x_pgn_fontpoints))
        self.tree.setHeaderLabels((_("Moves"), _("Opening")))

        bt_act = Controles.PB(self, _("Update"), self.bt_update, plano=False).ponIcono(Iconos.Pelicula_Seguir(), 16)
        self.lb_analisis = (
            Controles.LB(self, "").set_background("#C9D2D7").ponTipoLetra(puntos=configuration.x_pgn_fontpoints)
        )
        ly_act = Colocacion.H().control(bt_act).control(self.lb_analisis).relleno(1)

        layout = Colocacion.V().otro(ly_act).control(self.tree)
        self.setLayout(layout)

        self.dicItems = {}

    def seleccionado(self):
        item = self.tree.currentItem()
        if item:
            data_item = self.dicItems[str(item)]
            self.lb_analisis.set_text(data_item.game())
            lipv = data_item.listaPV()
            self.tabsAnalisis.panelOpening.goto_next_lipv(lipv)
        self.tree.resizeColumnToContents(0)

    def bt_update(self):
        self.tree.clear()

        dbop = self.tabsAnalisis.dbop
        levelbase = len(dbop.basePV.split(" "))

        def haz(trdata, iparent, nivel):
            for move, hijo in trdata.dicHijos.items():
                item = QtWidgets.QTreeWidgetItem(iparent)
                item.setText(0, hijo.pgn)
                item.setText(1, hijo.opening)
                hijo.item = item
                if nivel < (levelbase + 1):
                    item.setExpanded(True)
                self.dicItems[str(item)] = hijo
                haz(hijo, item, nivel + 1)

        self.tree_data = self.tabsAnalisis.dbop.totree()
        haz(self.tree_data, self.tree, 1)
        self.tree.resizeColumnToContents(0)

        self.lb_analisis.set_text("")

    def start(self):
        if len(self.dicItems) == 0:
            self.bt_update()

    def stop(self):
        pass

    def setData(self, data):
        pass

    def menuContexto(self, position):
        item = self.tree.currentItem()
        if not item:
            return

        menu = QTVarios.LCMenu(self)

        menu1 = menu.submenu(_("Expand"), Iconos.Mas22())
        menu1.opcion("expandall", _("All"), Iconos.PuntoVerde())
        menu1.separador()
        menu1.opcion("expandthis", _("This branch"), Iconos.PuntoAmarillo())
        menu.separador()
        menu1 = menu.submenu(_("Collapse"), Iconos.Menos22())
        menu1.opcion("collapseall", _("All"), Iconos.PuntoVerde())
        menu1.separador()
        menu1.opcion("collapsethis", _("This branch"), Iconos.PuntoAmarillo())
        resp = menu.lanza()
        if resp:
            if resp == "expandthis":
                quien, siExpand = item, True

            elif resp == "expandall":
                quien, siExpand = None, True

            elif resp == "collapsethis":
                quien, siExpand = item, False

            elif resp == "collapseall":
                quien, siExpand = None, False

        def work(data):
            item = data.item
            if item:
                item.setExpanded(siExpand)

            for uno, datauno in data.dicHijos.items():
                work(datauno)

        data = self.dicItems[str(quien)] if quien else self.tree_data
        work(data)
        self.tree.resizeColumnToContents(0)


class TabsAnalisis(QtWidgets.QWidget):
    def __init__(self, panelOpening, procesador, configuration):
        QtWidgets.QWidget.__init__(self)

        self.panelOpening = panelOpening
        self.dbop = panelOpening.dbop

        self.procesador = procesador
        self.configuration = configuration
        self.game = None
        self.njg = None

        self.tabtree = TabTree(self, configuration)
        self.tabengine = TabEngine(self, procesador, configuration)
        # self.tabengine.tabButton(0, QtWidgets.QTabBar.RightSide).deleteLater()
        # self.tabengine.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, 0)


        self.li_tabs = [("engine", self.tabengine), ("tree", self.tabtree)]
        self.tabActive = 0

        self.tabs = Controles.Tab(panelOpening)
        self.tabs.ponTipoLetra(puntos=self.configuration.x_pgn_fontpoints)
        self.tabs.setTabIcon(0, Iconos.Motor())
        self.tabs.nuevaTab(self.tabengine, _("Engine"))
        self.tabs.nuevaTab(self.tabtree, _("Tree"))
        self.tabs.setTabIcon(1, Iconos.Arbol())

        self.tabs.dispatchChange(self.tabChanged)

        tabButton = QtWidgets.QToolButton(self)
        tabButton.setIcon(Iconos.Nuevo())
        tabButton.clicked.connect(self.creaTab)
        li = [(_("Analysis of next move"), True), (_("Analysis of current move"), False)]
        self.cb_nextmove = Controles.CB(self, li, True).capture_changes(self.changedNextMove)

        corner_widget = QtWidgets.QWidget(self)
        lyCorner = Colocacion.H().control(self.cb_nextmove).control(tabButton).margen(0)
        corner_widget.setLayout(lyCorner)

        self.tabs.setCornerWidget(corner_widget)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.tabCloseRequested)

        self.tabs.quita_x(0)
        self.tabs.quita_x(1)

        layout = Colocacion.V()
        layout.control(self.tabs).margen(0)
        self.setLayout(layout)

    def changedNextMove(self):
        if self.game is not None:
            self.setPosicion(self.game, self.njg)

    def tabChanged(self, ntab):
        self.tabActive = ntab
        if ntab > 0:
            tipo, wtab = self.li_tabs[ntab]
            wtab.start()

    def tabCloseRequested(self, ntab):
        tipo, wtab = self.li_tabs[ntab]
        wtab.stop()
        if ntab > 1:
            del self.li_tabs[ntab]
            self.tabs.removeTab(ntab)
            del wtab

    def creaTab(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion("book", _("Polyglot book"), Iconos.Libros())
        menu.separador()
        menu.opcion("dbase", _("Database"), Iconos.Database())
        # menu.separador()
        # menu.opcion("tree", _("Tree"), Iconos.Arbol())
        resp = menu.lanza()
        pos = 0
        if resp == "book":
            book = self.seleccionaLibro()
            if book:
                tabbook = TabBook(self, book, self.configuration)
                self.li_tabs.append((resp, tabbook))
                pos = len(self.li_tabs) - 1
                self.tabs.nuevaTab(tabbook, book.name, pos)
                self.tabs.setTabIcon(pos, Iconos.Libros())
                self.setPosicion(self.game, self.njg, pos)

        # elif resp == "tree":
        #     tabtree = TabTree(self, self.configuration)
        #     self.li_tabs.append(("tree", tabtree))
        #     pos = len(self.li_tabs)-1
        #     self.tabs.nuevaTab(tabtree, _("Tree"), pos)
        #     self.tabs.setTabIcon(pos, Iconos.Arbol())
        #     tabtree.bt_update()

        elif resp == "dbase":
            nomfichgames = QTVarios.select_db(self, self.configuration, True, False)
            if nomfichgames:
                db_stat = DBgamesST.TreeSTAT(nomfichgames + ".st1")
                tabdb = TabDatabase(self, self.procesador, db_stat)
                self.li_tabs.append((resp, tabdb))
                pos = len(self.li_tabs) - 1
                self.setPosicion(self.game, self.njg, pos)
                name = os.path.basename(nomfichgames)[:-5]
                self.tabs.nuevaTab(tabdb, name, pos)
                self.tabs.setTabIcon(pos, Iconos.Database())
        self.tabs.activa(pos)

    def setPosicion(self, game, njg, numTab=None):
        if game is None:
            return
        move = game.move(njg)
        self.game = game
        self.njg = njg
        next = self.cb_nextmove.valor()
        if move:
            if njg == 0:
                pv = game.pv_hasta(njg) if next else ""
            else:
                pv = game.pv_hasta(njg if next else njg - 1)
            position = move.position if next else move.position_before
        else:
            position = Position.Position().set_pos_initial()
            pv = ""

        for ntab, (tipo, tab) in enumerate(self.li_tabs):
            if ntab == 0:
                p = Game.Game()
                p.read_pv(pv)
                tab.setData(p.pgn_html(with_figurines=self.configuration.x_pgn_withfigurines), position)
            else:
                data = pv if tipo == "dbase" else position
                if numTab is not None:
                    if ntab != numTab:
                        continue
                if ntab > 1:
                    tab.setData(data)
                    tab.start()

    def seleccionaLibro(self):
        list_books = Books.ListBooks()
        list_books.restore_pickle(self.configuration.file_books)
        list_books.check()
        menu = QTVarios.LCMenu(self)
        rondo = QTVarios.rondoPuntos()
        for book in list_books.lista:
            menu.opcion(("x", book), book.name, rondo.otro())
            menu.separador()
        menu.opcion(("n", None), _("Install new book"), Iconos.Nuevo())
        resp = menu.lanza()
        if resp:
            orden, book = resp
            if orden == "x":
                pass
            elif orden == "n":
                fbin = QTUtil2.leeFichero(self, list_books.path, "bin", titulo=_("Polyglot book"))
                if fbin:
                    list_books.path = os.path.dirname(fbin)
                    name = os.path.basename(fbin)[:-4]
                    book = Books.Book("P", name, fbin, True)
                    list_books.nuevo(book)
                    list_books.save_pickle(self.configuration.file_books)
        else:
            book = None
        return book

    def saveConfig(self):
        for tipo, wtab in self.li_tabs:
            if tipo == "engine":
                wtab.saveConfig()
