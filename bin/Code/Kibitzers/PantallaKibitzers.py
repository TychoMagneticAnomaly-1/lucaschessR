import os

from PySide2 import QtWidgets

from Code.Kibitzers import Kibitzers
from Code.Engines import Priorities
from Code.Polyglots import Books
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTVarios
from Code.QT import QTUtil2
from Code.QT import Delegados
from Code.QT import FormLayout


class WKibitzers(QTVarios.WDialogo):
    def __init__(self, w_parent, kibitzers_manager):
        titulo = _("Kibitzers")
        icono = Iconos.Kibitzer()
        extparam = "kibitzer"
        QTVarios.WDialogo.__init__(self, w_parent, titulo, icono, extparam)

        self.kibitzers_manager = kibitzers_manager
        self.configuracion = kibitzers_manager.configuracion
        self.procesador = kibitzers_manager.procesador

        self.tipos = Kibitzers.Tipos()

        self.kibitzers = Kibitzers.Kibitzers()
        self.liKibActual = []

        self.grid_kibitzers = None

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("New"), Iconos.Nuevo(), self.nuevo),
            None,
            (_("Remove"), Iconos.Borrar(), self.remove),
            None,
            (_("Copy"), Iconos.Copiar(), self.copy),
            None,
            (_("Up"), Iconos.Arriba(), self.up),
            None,
            (_("Down"), Iconos.Abajo(), self.down),
            None,
            (_("External engines"), Iconos.Motores(), self.ext_engines),
            None,
        )
        tb = Controles.TBrutina(self, li_acciones)

        self.splitter = QtWidgets.QSplitter(self)
        self.register_splitter(self.splitter, "kibitzers")

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva(
            "TIPO", "", 30, centered=True, edicion=Delegados.PmIconosBMT(self, dicIconos=self.tipos.dicDelegado())
        )
        o_columns.nueva("NOMBRE", _("Kibitzer"), 209)
        self.grid_kibitzers = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True, xid="kib")
        self.grid_kibitzers.tipoLetra(puntos=self.configuracion.x_pgn_fontpoints)
        self.register_grid(self.grid_kibitzers)

        w = QtWidgets.QWidget()
        ly = Colocacion.V().control(self.grid_kibitzers).margen(0)
        w.setLayout(ly)
        self.splitter.addWidget(w)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("CAMPO", _("Label"), 152, siDerecha=True)
        o_columns.nueva("VALOR", _("Value"), 390, edicion=Delegados.MultiEditor(self))
        self.gridValores = Grid.Grid(self, o_columns, siSelecFilas=False, xid="val", siEditable=True)
        self.gridValores.tipoLetra(puntos=self.configuracion.x_pgn_fontpoints)
        self.register_grid(self.gridValores)

        w = QtWidgets.QWidget()
        ly = Colocacion.V().control(self.gridValores).margen(0)
        w.setLayout(ly)
        self.splitter.addWidget(w)

        self.splitter.setSizes([259, 562])  # por defecto

        ly = Colocacion.V().control(tb).control(self.splitter)
        self.setLayout(ly)

        self.restore_video(anchoDefecto=849, altoDefecto=400)

        self.grid_kibitzers.gotop()

    def me_set_editor(self, parent):
        recno = self.gridValores.recno()
        key = self.liKibActual[recno][2]
        nk = self.krecno()
        kibitzer = self.kibitzers.kibitzer(nk)
        valor = control = lista = minimo = maximo = None
        if key is None:
            return None
        elif key == "name":
            control = "ed"
            valor = kibitzer.name
        elif key == "prioridad":
            control = "cb"
            lista = Priorities.priorities.combo()
            valor = kibitzer.prioridad
        elif key == "position_before":
            kibitzer.position_before = not kibitzer.position_before
            self.kibitzers.save()
            self.goto(nk)
        elif key == "visible":
            kibitzer.visible = not kibitzer.visible
            self.kibitzers.save()
            self.goto(nk)
        elif key == "info":
            control = "ed"
            valor = kibitzer.id_info
        elif key.startswith("opcion"):
            opcion = kibitzer.li_uci_options_editable()[int(key[7:])]
            tipo = opcion.tipo
            valor = opcion.valor
            if tipo == "spin":
                control = "sb"
                minimo = opcion.minimo
                maximo = opcion.maximo
            elif tipo in ("check", "button"):
                opcion.valor = not valor
                self.kibitzers.save()
                self.goto(nk)
            elif tipo == "combo":
                lista = [(var, var) for var in opcion.liVars]
                control = "cb"
            elif tipo == "string":
                control = "ed"

        self.me_control = control
        self.me_key = key

        if control == "ed":
            return Controles.ED(parent, valor)
        elif control == "cb":
            return Controles.CB(parent, lista, valor)
        elif control == "sb":
            return Controles.SB(parent, valor, minimo, maximo)
        return None

    def me_ponValor(self, editor, valor):
        if self.me_control == "ed":
            editor.setText(str(valor))
        elif self.me_control in ("cb", "sb"):
            editor.ponValor(valor)

    def me_leeValor(self, editor):
        if self.me_control == "ed":
            return editor.texto()
        elif self.me_control in ("cb", "sb"):
            return editor.valor()

    def grid_setvalue(self, grid, nfila, columna, valor):
        nk = self.krecno()
        kibitzer = self.kibitzers.kibitzer(nk)
        if self.me_key == "name":
            valor = valor.strip()
            if valor:
                kibitzer.name = valor
        elif self.me_key == "tipo":
            kibitzer.tipo = valor
        elif self.me_key == "prioridad":
            kibitzer.prioridad = valor
        elif self.me_key == "info":
            kibitzer.id_info = valor.strip()
        elif self.me_key.startswith("opcion"):
            opcion = kibitzer.li_uci_options_editable()[int(self.me_key[7:])]
            opcion.valor = valor
            kibitzer.ordenUCI(opcion.name, valor)
        self.kibitzers.save()
        self.goto(nk)

    def ext_engines(self):
        self.procesador.motoresExternos()

    def terminar(self):
        self.save_video()
        self.accept()

    def closeEvent(self, QCloseEvent):
        self.save_video()

    def nuevo(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion(("engine", None), _("Engine"), Iconos.Motor())
        menu.separador()

        submenu = menu.submenu(_("Book polyglot"), Iconos.Book())
        listaLibros = Books.ListaLibros()
        listaLibros.restore_pickle(self.configuracion.ficheroBooks)
        listaLibros.comprueba()
        rondo = QTVarios.rondoPuntos()
        for book in listaLibros.lista:
            submenu.opcion(("book", book), book.name, rondo.otro())
            submenu.separador()
        submenu.opcion(("installbook", None), _("Install new book"), Iconos.Nuevo())
        menu.separador()

        si_gaviota = True
        si_index = True
        for kib in self.kibitzers.lista:
            if kib.tipo == Kibitzers.KIB_GAVIOTA:
                si_gaviota = False
            elif kib.tipo == Kibitzers.KIB_INDEXES:
                si_index = False
        if si_index:
            menu.opcion(("index", None), _("Indexes") + " - RodentII", Iconos.Camara())
            menu.separador()
        if si_gaviota:
            menu.opcion(("gaviota", None), _("Gaviota Tablebases"), Iconos.Finales())

        resp = menu.lanza()
        if resp:
            orden, extra = resp

            if orden == "engine":
                self.nuevo_engine()
            elif orden in "book":
                num = self.kibitzers.nuevo_polyglot(extra)
                self.goto(num)
            elif orden == "gaviota":
                num = self.kibitzers.nuevo_gaviota()
                self.goto(num)
            elif orden == "index":
                num = self.kibitzers.nuevo_index()
                self.goto(num)
            elif orden in "installbook":
                self.polyglot_install(listaLibros)

    def polyglot_install(self, listaLibros):
        fbin = QTUtil2.leeFichero(self, listaLibros.path, "bin", titulo=_("Polyglot book"))
        if fbin:
            listaLibros.path = os.path.dirname(fbin)
            name = os.path.basename(fbin)[:-4]
            book = Books.Libro("P", name, fbin, True)
            listaLibros.nuevo(book)
            listaLibros.save_pickle(self.configuracion.ficheroBooks)
            num = self.kibitzers.nuevo_polyglot(book)
            self.goto(num)

    def nuevo_engine(self):
        form = FormLayout.FormLayout(self, _("Kibitzer"), Iconos.Kibitzer(), anchoMinimo=340)

        form.edit(_("Name"), "")
        form.separador()

        form.combobox(_("Engine"), self.configuracion.comboMotores(), "stockfish")
        form.separador()

        liTipos = Kibitzers.Tipos().comboSinIndices()
        form.combobox(_("Type"), liTipos, Kibitzers.KIB_CANDIDATES)
        form.separador()

        form.combobox(_("Process priority"), Priorities.priorities.combo(), Priorities.priorities.normal)
        form.separador()

        resultado = form.run()

        if resultado:
            accion, resp = resultado

            name, engine, tipo, prioridad = resp

            # Indexes only with Rodent II
            if tipo == "I":
                engine = "rodentII"
                if not name:  # para que no repita rodent II
                    name = _("Indexes") + " - RodentII"

            name = name.strip()
            if not name:
                for label, key in liTipos:
                    if key == tipo:
                        name = "%s: %s" % (label, engine)
            num = self.kibitzers.nuevo_engine(name, engine, tipo, prioridad)
            self.goto(num)

    def remove(self):
        if self.kibitzers.lista:
            num = self.krecno()
            kib = self.kibitzers.kibitzer(num)
            if QTUtil2.pregunta(self, _("Are you sure?") + "\n %s" % kib.name):
                self.kibitzers.remove(num)
                self.grid_kibitzers.refresh()
                nk = len(self.kibitzers)
                if nk > 0:
                    if num > nk:
                        num = nk - 1
                    self.goto(num)

    def copy(self):
        num = self.krecno()
        if num >= 0:
            num = self.kibitzers.clonar(num)
            self.goto(num)

    def goto(self, num):
        if self.grid_kibitzers:
            self.grid_kibitzers.goto(num, 0)
            self.grid_kibitzers.refresh()
            self.actKibitzer()
            self.gridValores.refresh()

    def krecno(self):
        return self.grid_kibitzers.recno()

    def up(self):
        num = self.kibitzers.up(self.krecno())
        if num is not None:
            self.goto(num)

    def down(self):
        num = self.kibitzers.down(self.krecno())
        if num is not None:
            self.goto(num)

    def grid_num_datos(self, grid):
        gid = grid.id
        if gid == "kib":
            return len(self.kibitzers)
        return len(self.liKibActual)

    def grid_dato(self, grid, fila, oColumna):
        columna = oColumna.clave
        gid = grid.id
        if gid == "kib":
            return self.gridDatoKibitzers(fila, columna)
        elif gid == "val":
            return self.gridDatoValores(fila, columna)

    def gridDatoKibitzers(self, fila, columna):
        me = self.kibitzers.kibitzer(fila)
        if columna == "NOMBRE":
            return me.name
        elif columna == "TIPO":
            return me.tipo

    def gridDatoValores(self, fila, columna):
        li = self.liKibActual[fila]
        if columna == "CAMPO":
            return li[0]
        else:
            return li[1]

    def grid_cambiado_registro(self, grid, fila, columna):
        if grid.id == "kib":
            self.goto(fila)

    def grid_doble_click(self, grid, fila, columna):
        if grid.id == "kib":
            self.terminar()

            self.kibitzers_manager.run_new(fila)

    def actKibitzer(self):
        self.liKibActual = []
        fila = self.krecno()
        if fila < 0:
            return

        me = self.kibitzers.kibitzer(fila)
        tipo = me.tipo
        self.liKibActual.append((_("Name"), me.name, "name"))

        if not (tipo in (Kibitzers.KIB_POLYGLOT, Kibitzers.KIB_GAVIOTA, Kibitzers.KIB_INDEXES)):
            self.liKibActual.append((_("Type"), me.ctipo(), "tipo"))
            self.liKibActual.append((_("Priority"), me.cpriority(), "prioridad"))

        self.liKibActual.append((_("Analysis of the base position"), str(me.position_before), "position_before"))
        self.liKibActual.append((_("Visible in menu"), str(me.visible), "visible"))

        if not (tipo in (Kibitzers.KIB_POLYGLOT, Kibitzers.KIB_GAVIOTA, Kibitzers.KIB_INDEXES)):
            self.liKibActual.append((_("Engine"), me.name, None))

        if not (tipo in (Kibitzers.KIB_POLYGLOT,)):
            self.liKibActual.append((_("Author"), me.autor, None))

        if not (tipo in (Kibitzers.KIB_GAVIOTA, Kibitzers.KIB_INDEXES)):
            self.liKibActual.append((_("File"), me.path_exe, None))

        if not (tipo in (Kibitzers.KIB_POLYGLOT, Kibitzers.KIB_GAVIOTA, Kibitzers.KIB_INDEXES)):
            self.liKibActual.append((_("Information"), me.id_info, "info"))

            for num, opcion in enumerate(me.li_uci_options_editable()):
                default = opcion.label_default()
                label_default = " (%s)" % default if default else ""
                valor = str(opcion.valor)
                if opcion.tipo in ("check", "button"):
                    valor = valor.lower()
                self.liKibActual.append(("%s%s" % (opcion.name, label_default), valor, "opcion,%d" % num))


class WKibitzerLive(QTVarios.WDialogo):
    def __init__(self, wParent, configuracion, numkibitzer):
        self.kibitzers = Kibitzers.Kibitzers()
        self.kibitzer = self.kibitzers.kibitzer(numkibitzer)
        titulo = self.kibitzer.name
        icono = Iconos.Kibitzer()
        extparam = "kibitzerlive"
        QTVarios.WDialogo.__init__(self, wParent, titulo, icono, extparam)

        self.configuracion = configuracion

        self.li_options = self.leeOpciones()
        self.liOriginal = self.leeOpciones()

        li_acciones = (
            (_("Save"), Iconos.Grabar(), self.grabar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
        )
        tb = Controles.TBrutina(self, li_acciones)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("CAMPO", _("Label"), 152, siDerecha=True)
        o_columns.nueva("VALOR", _("Value"), 390, edicion=Delegados.MultiEditor(self))
        self.gridValores = Grid.Grid(self, o_columns, siSelecFilas=False, xid="val", siEditable=True)
        self.gridValores.tipoLetra(puntos=self.configuracion.x_pgn_fontpoints)
        self.register_grid(self.gridValores)

        ly = Colocacion.V().control(tb).control(self.gridValores)
        self.setLayout(ly)

        self.restore_video(anchoDefecto=600, altoDefecto=400)

        self.gridValores.gotop()

        # self.gridValores.resizeRowsToContents()

    def leeOpciones(self):
        li = []
        li.append([_("Priority"), self.kibitzer.cpriority(), "prioridad"])
        li.append([_("Analysis of the base position"), str(self.kibitzer.position_before), "position_before"])
        for num, opcion in enumerate(self.kibitzer.li_uci_options()):
            default = opcion.label_default()
            label_default = " (%s)" % default if default else ""
            valor = str(opcion.valor)
            if opcion.tipo in ("check", "button"):
                valor = valor.lower()
            li.append(["%s%s" % (opcion.name, label_default), valor, "%d" % num])
        return li

    def grabar(self):
        self.kibitzers.save()
        lidif_opciones = []
        xprioridad = None
        xposicionBase = None
        for x in range(len(self.li_options)):
            if self.li_options[x][1] != self.liOriginal[x][1]:
                key = self.li_options[x][2]
                if key == "prioridad":
                    prioridad = self.kibitzer.prioridad
                    priorities = Priorities.priorities
                    xprioridad = priorities.value(prioridad)
                elif key == "position_before":
                    xposicionBase = self.kibitzer.position_before
                else:
                    numopcion = int(key)
                    opcion = self.kibitzer.li_options[numopcion]
                    lidif_opciones.append((opcion.name, opcion.valor))

        self.result_xprioridad = xprioridad
        self.result_opciones = lidif_opciones
        self.result_posicionBase = xposicionBase
        self.save_video()
        self.accept()

    def me_set_editor(self, parent):
        recno = self.gridValores.recno()
        key = self.li_options[recno][2]
        control = lista = minimo = maximo = None
        if key == "prioridad":
            control = "cb"
            lista = Priorities.priorities.combo()
            valor = self.kibitzer.prioridad
        elif key == "position_before":
            self.kibitzer.position_before = not self.kibitzer.position_before
            self.li_options[recno][1] = self.kibitzer.position_before
            self.gridValores.refresh()
        else:
            opcion = self.kibitzer.li_options[int(key)]
            tipo = opcion.tipo
            valor = opcion.valor
            if tipo == "spin":
                control = "sb"
                minimo = opcion.min
                maximo = opcion.max
            elif tipo in ("check", "button"):
                opcion.valor = not valor
                self.li_options[recno][1] = opcion.valor
                self.gridValores.refresh()
            elif tipo == "combo":
                lista = [(var, var) for var in opcion.liVars]
                control = "cb"
            elif tipo == "string":
                control = "ed"

        self.me_control = control
        self.me_key = key

        if control == "ed":
            return Controles.ED(parent, valor)
        elif control == "cb":
            return Controles.CB(parent, lista, valor)
        elif control == "sb":
            return Controles.SB(parent, valor, minimo, maximo)
        return None

    def me_ponValor(self, editor, valor):
        if self.me_control == "ed":
            editor.setText(str(valor))
        elif self.me_control in ("cb", "sb"):
            editor.ponValor(valor)

    def me_leeValor(self, editor):
        if self.me_control == "ed":
            return editor.texto()
        elif self.me_control in ("cb", "sb"):
            return editor.valor()

    def grid_setvalue(self, grid, nfila, columna, valor):
        if self.me_key == "prioridad":
            self.kibitzer.prioridad = valor
        else:
            nopcion = int(self.me_key)
            opcion = self.kibitzer.li_options[nopcion]
            opcion.valor = valor
            self.li_options[nopcion + 1][1] = valor
            self.kibitzer.ordenUCI(opcion.name, valor)

    def grid_num_datos(self, grid):
        return len(self.li_options)

    def grid_dato(self, grid, fila, oColumna):
        columna = oColumna.clave
        li = self.li_options[fila]
        if columna == "CAMPO":
            return li[0]
        else:
            return li[1]