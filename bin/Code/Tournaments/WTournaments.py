import os
import shutil
import time

from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code import Util
from Code.Tournaments import WTournament
import Code

GRID_ALIAS, GRID_VALUES, GRID_GAMES_QUEUED, GRID_GAMES_FINISHED, GRID_RESULTS = range(5)


class WTournaments(QTVarios.WDialogo):
    def __init__(self, wParent):

        titulo = _("Tournaments between engines")
        icono = Iconos.Torneos()
        extparam = "torneos"
        QTVarios.WDialogo.__init__(self, wParent, titulo, icono, extparam)

        self.configuracion = Code.configuracion

        self.play_torneo = None

        # Datos
        self.lista = self.leeTorneos()
        self.xjugar = None

        # Toolbar
        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("New"), Iconos.Nuevo(), self.crear),
            None,
            (_("Open"), Iconos.Modificar(), self.lanzar),
            None,
            (_("Rename"), Iconos.Rename(), self.rename),
            None,
            (_("Copy"), Iconos.Copiar(), self.copiar),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        # grid
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NOMBRE", _("Name"), 240)
        o_columns.nueva("FECHA", _("Date"), 120, centered=True)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True)
        self.register_grid(self.grid)

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).margen(8)
        self.setLayout(layout)

        self.restore_video(siTam=True, anchoDefecto=400, altoDefecto=500)

        self.grid.gotop()

    def leeTorneos(self):
        li = []
        carpeta = self.configuracion.folder_tournaments()
        for entry in Util.listdir(carpeta):
            filename = entry.name
            if filename.lower().endswith(".mvm"):
                st = entry.stat()
                li.append((filename, st.st_ctime, st.st_mtime))

        li = sorted(li, key=lambda x: x[2], reverse=True)  # por ultima modificacin y al reves
        return li

    def refresh_lista(self):
        self.lista = self.leeTorneos()
        self.grid.refresh()

    def nom_torneo_pos(self, fila):
        return self.lista[fila][0][:-4]

    def grid_num_datos(self, grid):
        return len(self.lista)

    def grid_dato(self, grid, fila, oColumna):
        columna = oColumna.clave
        name, fcreacion, fmanten = self.lista[fila]
        if columna == "NOMBRE":
            return name[:-4]
        elif columna == "FECHA":
            tm = time.localtime(fmanten)
            return "%d-%02d-%d, %2d:%02d" % (tm.tm_mday, tm.tm_mon, tm.tm_year, tm.tm_hour, tm.tm_min)

    def terminar(self):
        self.save_video()
        self.accept()

    def grid_doble_click(self, grid, fila, columna):
        self.lanzar()

    def lanzar(self):
        n = self.grid.recno()
        if n >= 0:
            self.trabajar(self.nom_torneo_pos(n))
            self.accept()

    def edit_name(self, previo):
        liGen = [(None, None)]
        liGen.append((_("Name") + ":", previo))
        resultado = FormLayout.fedit(liGen, title=_("Tournaments between engines"), parent=self, icon=Iconos.Torneos())
        nom_torneo = None
        if resultado:
            accion, liGen = resultado
            nom_torneo = Util.valid_filename(liGen[0].strip())
            if nom_torneo:
                path = os.path.join(self.configuracion.folder_tournaments(), nom_torneo + ".mvm")
                if os.path.isfile(path):
                    QTUtil2.message_error(self, _("The file %s already exist") % nom_torneo)
        return nom_torneo

    def crear(self):
        nom_torneo = self.edit_name("")
        if nom_torneo:
            self.trabajar(nom_torneo)

    def trabajar(self, nom_torneo):
        self.play_torneo = os.path.join(self.configuracion.folder_tournaments(), "%s.mvm" % nom_torneo)
        self.accept()

    def rename(self):
        fila = self.grid.recno()
        if fila >= 0:
            nom_origen = self.nom_torneo_pos(fila)
            nom_destino = self.edit_name(nom_origen)
            if nom_origen != nom_destino:
                path_origen = os.path.join(self.configuracion.folder_tournaments(), "%s.mvm" % nom_origen)
                path_destino = os.path.join(self.configuracion.folder_tournaments(), "%s.mvm" % nom_destino)
                shutil.move(path_origen, path_destino)
                self.refresh_lista()

    def borrar(self):
        fila = self.grid.recno()
        if fila >= 0:
            name = self.nom_torneo_pos(fila)
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), name)):
                path = os.path.join(self.configuracion.folder_tournaments(), "%s.mvm" % name)
                os.remove(path)
                self.refresh_lista()

    def copiar(self):
        fila = self.grid.recno()
        if fila >= 0:
            nom_origen = self.nom_torneo_pos(fila)
            nom_destino = self.edit_name(nom_origen)
            if nom_origen != nom_destino:
                path_origen = os.path.join(self.configuracion.folder_tournaments(), "%s.mvm" % nom_origen)
                path_destino = os.path.join(self.configuracion.folder_tournaments(), "%s.mvm" % nom_destino)
                shutil.copy(path_origen, path_destino)
                self.refresh_lista()


def tournaments(parent):
    w = WTournaments(parent)
    if w.exec_():
        if w.play_torneo:
            w = WTournament.WTournament(parent, w.play_torneo)
            w.exec_()