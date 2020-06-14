import operator
import os.path
import pickle

from PySide2 import QtWidgets
from PySide2.QtCore import Qt

import Code
from Code import ConfBoards
from Code import TrListas
from Code import Translate
from Code import Util
from Code.SQL import UtilSQL
from Code.Constantes import MENU_PLAY_BOTH, POS_TUTOR_HORIZONTAL

import OSEngines  # in OS folder


LCFILEFOLDER: str = os.path.realpath("../lc.folder")
LCBASEFOLDER: str = os.path.realpath("../UserData")


def int_toolbutton(xint):
    for tbi in (Qt.ToolButtonIconOnly, Qt.ToolButtonTextOnly, Qt.ToolButtonTextBesideIcon, Qt.ToolButtonTextUnderIcon):
        if xint == int(tbi):
            return tbi
    return Qt.ToolButtonTextUnderIcon


def toolbutton_int(qt_tbi):
    for tbi in (Qt.ToolButtonIconOnly, Qt.ToolButtonTextOnly, Qt.ToolButtonTextBesideIcon, Qt.ToolButtonTextUnderIcon):
        if qt_tbi == tbi:
            return int(tbi)
    return int(Qt.ToolButtonTextUnderIcon)


def active_folder():
    if os.path.isfile(LCFILEFOLDER):
        with open(LCFILEFOLDER, "wt") as f:
            x = f.read().strip()
            if os.path.isdir(x):
                return x
    return LCBASEFOLDER


def is_default_folder():
    return active_folder() == os.path.abspath(LCBASEFOLDER)


def change_folder(nueva):
    if nueva:
        if os.path.abspath(nueva) == os.path.abspath(LCBASEFOLDER):
            return change_folder(None)
        with open(LCFILEFOLDER, "wt") as f:
            f.write(nueva)
    else:
        Util.remove_file(LCFILEFOLDER)


class Perfomance:
    def __init__(self):
        self.limit_max = 3500.0
        self.limit_min = 800.0
        self.lost_factor = 15.0
        self.lost_exp = 1.35

        self.very_bad_lostp = 200
        self.bad_lostp = 90
        self.bad_limit_min = 1200.0
        self.very_bad_factor = 8
        self.bad_factor = 2

        self.very_good_depth = 6
        self.good_depth = 3

    def elo(self, xlost):
        # 3500.0 - ((60 * xlost) / (xgmo ** 0.4)) + abs(xeval ** 0.8)
        return min(
            max(int(self.limit_max - self.lost_factor * (xlost ** self.lost_exp)), self.limit_min), self.limit_max
        )

    def elo_bad_vbad(self, xlost):
        elo = self.elo(xlost)
        vbad = xlost > self.very_bad_lostp
        bad = False if vbad else xlost > self.bad_lostp
        return elo, bad, vbad

    def limit(self, verybad, bad, nummoves):
        if verybad or bad:
            return int(
                max(
                    self.limit_max
                    - self.very_bad_factor * 1000.0 * verybad / nummoves
                    - self.bad_factor * 1000.0 * bad / nummoves,
                    self.bad_limit_min,
                )
            )
        else:
            return self.limit_max

    def save_dic(self):
        dic = {}
        default = Perfomance()
        for x in dir(self):
            if not x.startswith("_"):
                atr = getattr(self, x)
                if not callable(atr):
                    if atr != getattr(default, x):
                        dic[x] = atr
        return dic

    def restore_dic(self, dic):
        for x in dir(self):
            if x in dic:
                setattr(self, x, dic[x])

    def save(self):
        dic = self.save_dic()
        return str(dic)

    def restore(self, txt):
        if txt:
            dic = eval(txt)
            self.restore_dic(dic)


class BoxRooms:
    def __init__(self, configuracion):
        self.file = os.path.join(configuracion.carpeta_config, "boxrooms.pk")
        self._list = self.read()

    def read(self):
        obj = Util.restore_pickle(self.file)
        return [] if obj is None else obj

    def write(self):
        Util.save_pickle(self.file, self._list)

    def lista(self):
        return self._list

    def delete(self, num):
        del self._list[num]
        self.write()

    def append(self, carpeta, boxroom):
        self._list.append((carpeta, boxroom))
        self.write()


class Configuracion:
    def __init__(self, user):

        self.carpetaBase = active_folder()

        self.carpetaUsers = os.path.join(self.carpetaBase, "users")

        if user:
            Util.create_folder(self.carpetaUsers)
            self.carpeta = os.path.join(self.carpetaUsers, user)
            Util.create_folder(self.carpeta)
        else:
            Util.create_folder(self.carpetaBase)
            self.carpeta = self.carpetaBase

        self.carpeta_config = os.path.join(self.carpeta, "__Config__")
        Util.create_folder(self.carpeta_config)

        self.carpeta_results = os.path.join(self.carpeta, "Results")
        Util.create_folder(self.carpeta_results)

        self.user = user
        self.set_folders()

        self.is_main = user == ""

        self.version = ""

        self.x_id = Util.new_id()
        self.x_player = ""
        self.x_save_folder = ""
        self.x_save_pgn = ""
        self.x_save_lcsb = ""
        self.x_translator = ""
        self.x_style = "Fusion"
        self.x_tutor_view = POS_TUTOR_HORIZONTAL

        self.x_show_effects = False
        self.x_pieces_speed = 100
        self.x_save_tutor_variations = True

        self.x_mouse_shortcuts = False  # predictivo=True
        self.x_show_candidates = False

        self.x_captures_activate = False
        self.x_info_activate = False

        self.x_default_tutor_active = True

        self.x_elo = 0
        self.x_michelo = 1600
        self.x_fics = 1200
        self.x_fide = 1600
        self.x_lichess = 1600

        self.x_dgt = False

        self.x_menu_play = MENU_PLAY_BOTH

        self.x_opacity_tool_board = 10
        self.x_position_tool_board = "T"

        self.x_director_icon = False
        self.x_direct_graphics = True

        self.colores_nags_defecto()

        self.x_sizefont_infolabels = 10

        self.x_pgn_selbackground = None
        self.x_pgn_headerbackground = None

        self.x_pgn_width = 283
        self.x_pgn_fontpoints = 10
        self.x_pgn_rowheight = 28
        self.x_pgn_withfigurines = True

        self.x_pgn_english = False

        self.x_autopromotion_q = True

        # self.x_capture_option = "D"

        self.x_font_family = ""

        self.x_menu_points = 11
        self.x_menu_bold = False

        self.x_tb_fontpoints = 11
        self.x_tb_bold = False
        self.x_tb_icons = toolbutton_int(Qt.ToolButtonTextUnderIcon)

        self.x_cursor_thinking = True

        self.x_salvar_ganados = False
        self.x_salvar_perdidos = False
        self.x_salvar_abandonados = False
        self.x_salvar_pgn = ""

        self.x_salvar_csv = ""

        self.x_rival_inicial = "rocinante" if Code.isLinux else "irina"

        self.tutor_inicial = "honey"
        self.x_tutor_clave = self.tutor_inicial
        self.x_tutor_multipv = 10  # 0: maximo
        self.x_tutor_difpoints = 0
        self.x_tutor_difporc = 0
        self.x_tutor_mstime = 3000
        self.x_tutor_depth = 0

        self.x_sound_beep = False
        self.x_sound_our = False
        self.x_sound_move = False
        self.x_sound_results = False

        self.x_interval_replay = 1400

        self.x_engine_notbackground = False

        self.x_check_for_update = False

        self.x_log_engines = False

        self.x_carpeta_gaviota = self.carpeta_gaviota_defecto()

        self.palette = {}

        self.perfomance = Perfomance()

        self.li_favoritos = None

        self.liPersonalidades = []

        self.folder_internal_engines = os.path.join(Code.folder_OS, "Engines")
        self.dic_engines = OSEngines.read_engines(self.folder_internal_engines)

        self.lee_motores_externos()

        self.rival = self.buscaRival(self.x_rival_inicial)
        self.tutor = self.buscaTutor(self.tutor_inicial)
        if self.tutor.clave != self.x_tutor_clave:
            self.x_tutor_clave = self.tutor.clave

        self.siAplazada = False

    def boxrooms(self):
        return BoxRooms(self)

    def save_lcsb(self, nuevo=None):
        if nuevo:
            self.x_save_lcsb = nuevo
        return self.x_save_lcsb if self.x_save_lcsb else self.carpeta

    def nom_player(self):
        return _("Player") if not self.x_player else self.x_player

    def pgn_selbackground(self):
        return self.x_pgn_selbackground if self.x_pgn_selbackground else "#51708C"

    def pgn_headerbackground(self):
        return self.x_pgn_headerbackground if self.x_pgn_headerbackground else "#EDEDE4"

    def carpeta_gaviota_defecto(self):
        return os.path.relpath(Code.path_resource("Gaviota"))

    def carpeta_gaviota(self):
        if not Util.exist_file(os.path.join(self.x_carpeta_gaviota, "kbbk.gtb.cp4")):
            self.x_carpeta_gaviota = self.carpeta_gaviota_defecto()
            self.graba()
        return self.x_carpeta_gaviota

    def piezas_gaviota(self):
        if Util.exist_file(os.path.join(self.carpeta_gaviota(), "kbbkb.gtb.cp4")):
            return 5
        return 4

    def set_player(self, value):
        self.x_player = value

    def translator(self):
        return self.x_translator if self.x_translator else "en"

    def set_translator(self, xtranslator):
        self.x_translator = xtranslator

    def tipoIconos(self):
        return int_toolbutton(self.x_tb_icons)

    def set_tipoIconos(self, qtv):
        self.x_tb_icons = toolbutton_int(qtv)

    def start(self):
        self.lee()
        self.leeConfTableros()

    def changeActiveFolder(self, nueva):
        change_folder(nueva)
        self.set_folders()  # Siempre sera el principal
        self.lee()

    def create_base_folder(self, folder):
        folder = os.path.realpath(os.path.join(self.carpeta, folder))
        Util.create_folder(folder)
        return folder

    def file_competition_with_tutor(self):
        return os.path.join(self.carpeta_results, "CompetitionWithTutor.db")

    def folder_tournaments(self):
        return self.create_base_folder("Tournaments")

    def folder_tournaments_workers(self):
        return self.create_base_folder("Tournaments/Workers")

    def folder_openings(self):
        dic = self.leeVariables("OPENING_LINES")
        folder = dic.get("FOLDER", self.folderBaseOpenings)
        return folder if os.path.isdir(folder) else self.folderBaseOpenings

    def set_folder_openings(self, new_folder):
        new_folder = os.path.relpath(os.path.realpath(new_folder))
        dic = self.leeVariables("OPENING_LINES")
        dic["FOLDER"] = new_folder
        self.escVariables("OPENING_LINES", dic)

    def file_mate(self, mate):
        return os.path.join(self.carpeta_results, "Mate%d.pk" % mate)

    def file_endings_gtb(self):
        return os.path.join(self.carpeta_results, "EndingsGTB.db")

    def file_external_engines(self):
        return os.path.join(self.carpeta_config, "ExtEngines.pk")

    def file_kibitzers(self):
        return os.path.join(self.carpeta_config, "kibitzers.pk")

    def file_adjourns(self):
        return os.path.join(self.carpeta_config, "adjourns.ddb")

    def file_pers_openings(self):
        return os.path.join(self.carpeta_config, "persaperturas.pkd")

    def file_captures(self):
        return os.path.join(self.carpeta_results, "Captures.db")

    def file_counts(self):
        return os.path.join(self.carpeta_results, "Counts.db")

    def file_mate15(self):
        return os.path.join(self.carpeta_results, "Mate15.db")

    def folder_databases(self):
        return self.create_base_folder("Databases")

    def folder_databases_pgn(self):
        return self.create_base_folder("TemporaryDatabases")

    def folder_polyglots_factory(self):
        return self.create_base_folder("PolyglotsFactory")

    def opj_config(self, file):
        return os.path.join(self.carpeta_config, file)

    def file_video(self):
        return self.opj_config("confvid.pkd")

    def file_sounds(self):
        return self.opj_config("sounds.pkd")

    def file_param_analysis(self):
        return self.opj_config("paranalisis.pkd")

    def set_folders(self):

        self.fichero = os.path.join(self.carpeta_config, "lk.pk2")

        self.siPrimeraVez = not Util.exist_file(self.fichero)

        self.fichEstadElo = "%s/estad.pkli" % self.carpeta_results
        self.fichEstadMicElo = "%s/estadMic.pkli" % self.carpeta_results
        self.fichEstadFicsElo = "%s/estadFics.pkli" % self.carpeta_results
        self.fichEstadFideElo = "%s/estadFide.pkli" % self.carpeta_results
        self.fichEstadLichessElo = "%s/estadLichess.pkli" % self.carpeta_results
        self.ficheroBooks = "%s/books.lkv" % self.carpeta_config
        self.ficheroTrainBooks = "%s/booksTrain.lkv" % self.carpeta_results
        self.ficheroMemoria = "%s/memo.pk" % self.carpeta_results
        self.ficheroEntMaquina = "%s/entmaquina.pke" % self.carpeta_results
        self.ficheroEntMaquinaConf = "%s/entmaquinaconf.pkd" % self.carpeta_config
        self.ficheroGM = "%s/gm.pke" % self.carpeta_config
        self.ficheroGMhisto = "%s/gmh.db" % self.carpeta_results
        self.ficheroPuntuacion = "%s/punt.pke" % self.carpeta_results
        self.ficheroDirSound = "%s/direc.pkv" % self.carpeta_config
        self.ficheroEntAperturas = "%s/entaperturas.pkd" % self.carpeta
        self.ficheroEntAperturasPar = "%s/entaperturaspar.pkd" % self.carpeta
        self.ficheroDailyTest = "%s/nivel.pkd" % self.carpeta_results
        self.ficheroTemas = "%s/themes.pkd" % self.carpeta_config
        self.dirPersonalTraining = "%s/Personal Training" % self.carpeta
        self.ficheroBMT = "%s/lucas.bmt" % self.carpeta_results
        self.ficheroPotencia = "%s/power.db" % self.carpeta_results
        self.ficheroPuente = "%s/bridge.db" % self.carpeta_results
        self.ficheroMoves = "%s/moves.dbl" % self.carpeta_results
        self.ficheroRecursos = "%s/recursos.dbl" % self.carpeta_config
        self.ficheroFEN = self.ficheroRecursos
        self.ficheroConfTableros = "%s/confTableros.pk" % self.carpeta_config
        self.ficheroBoxing = "%s/boxing.pk" % self.carpeta_results
        self.ficheroTrainings = "%s/trainings.pk" % self.carpeta_results
        self.ficheroHorses = "%s/horses.db" % self.carpeta_results
        self.ficheroLearnPGN = "%s/LearnPGN.db" % self.carpeta_results
        self.ficheroPlayPGN = "%s/PlayPGN.db" % self.carpeta_results
        self.ficheroAlbumes = "%s/albumes.pkd" % self.carpeta_results
        self.ficheroPuntuaciones = "%s/hpoints.pkd" % self.carpeta_results
        self.ficheroAnotar = "%s/anotar.db" % self.carpeta_config

        self.ficheroSelectedPositions = "%s/Selected positions.fns" % self.dirPersonalTraining
        self.ficheroPresentationPositions = "%s/Challenge 101.fns" % self.dirPersonalTraining

        self.ficheroVariables = "%s/Variables.pk" % self.carpeta_config

        self.ficheroFiltrosPGN = "%s/pgnFilters.db" % self.carpeta_config

        Util.create_folder(self.dirPersonalTraining)

        Util.create_folder(self.folder_databases())

        self.carpetaSTS = "%s/STS" % self.carpeta

        self.carpetaScanners = "%s/%s" % (self.carpeta, "Scanners")
        Util.create_folder(self.carpetaScanners)

        self.ficheroExpeditions = "%s/Expeditions.db" % self.carpeta_results
        self.ficheroSingularMoves = "%s/SingularMoves.db" % self.carpeta_results

        if not Util.exist_file(self.ficheroRecursos):
            Util.file_copy(Code.path_resource("IntFiles", "recursos.dbl"), self.ficheroRecursos)

        self.folderBaseOpenings = os.path.join(self.carpeta, "OpeningLines")
        Util.create_folder(self.folderBaseOpenings)

    def compruebaBMT(self):
        if not Util.exist_file(self.ficheroBMT):
            self.ficheroBMT = "%s/lucas.bmt" % self.carpeta_results

    def limpia(self, name):
        self.elo = 0
        self.michelo = 1600
        self.fics = 1200
        self.fide = 1600
        self.x_id = Util.new_id()
        self.x_player = name
        self.x_save_folder = ""
        self.x_save_pgn = ""
        self.x_save_lcsb = ""

        self.x_salvar_ganados = False
        self.x_salvar_perdidos = False
        self.x_salvar_abandonados = False
        self.x_salvar_pgn = ""

        self.x_captures_activate = False
        self.x_info_activate = False
        self.x_mouse_shortcuts = False
        self.x_show_candidates = False

        self.x_salvar_csv = ""

        self.rival = self.buscaRival(self.x_rival_inicial)

        self.perfomance = Perfomance()

    def buscaRival(self, clave, defecto=None):
        if clave in self.dic_engines:
            return self.dic_engines[clave]
        if defecto is None:
            defecto = self.x_rival_inicial
        return self.buscaRival(defecto)

    def buscaTutor(self, clave):
        if clave in self.dic_engines:
            eng = self.dic_engines[clave]
            if eng.puedeSerTutor() and Util.exist_file(eng.path_exe):
                return eng
        return self.buscaTutor(self.tutor_inicial)

    def ayudaCambioTutor(self):  # TODO remove
        li = []
        for clave, cm in self.dic_engines.items():
            if cm.puedeSerTutor():
                li.append((clave, cm.nombre_ext()))
        li = sorted(li, key=operator.itemgetter(1))
        li.insert(0, self.tutor.clave)
        return li

    def listaCambioTutor(self):
        li = []
        for clave, cm in self.dic_engines.items():
            if cm.puedeSerTutor():
                li.append((cm.nombre_ext(), clave))
        li = sorted(li, key=operator.itemgetter(1))
        return li

    def comboMotores(self):
        li = []
        for clave, cm in self.dic_engines.items():
            li.append((cm.nombre_ext(), clave))
        li.sort(key=lambda x: x[0])
        return li

    def comboMotoresMultiPV10(self, minimo=10):  # %#
        liMotores = []
        for clave, cm in self.dic_engines.items():
            if cm.multiPV >= minimo:
                liMotores.append((cm.nombre_ext(), clave))

        li = sorted(liMotores, key=operator.itemgetter(0))
        return li

    def ayudaCambioCompleto(self, cmotor):
        li = []
        for clave, cm in self.dic_engines.items():
            li.append((clave, cm.nombre_ext()))
        li = sorted(li, key=operator.itemgetter(1))
        li.insert(0, cmotor)
        return li

    def estilos(self):
        li = [(x, x) for x in QtWidgets.QStyleFactory.keys()]
        return li

    def colores_nags_defecto(self):
        self.x_color_nag1 = "#0707FF"
        self.x_color_nag2 = "#FF7F00"
        self.x_color_nag3 = "#820082"
        self.x_color_nag4 = "#FF0606"
        self.x_color_nag5 = "#008500"
        self.x_color_nag6 = "#ECC70A"

    def graba(self):
        dic = {}
        for x in dir(self):
            if x.startswith("x_"):
                dic[x] = getattr(self, x)
        Util.save_pickle(self.fichero, dic)

    def lee(self):
        dic = Util.restore_pickle(self.fichero)
        if dic:
            for x in dir(self):
                if x.startswith("x_"):
                    if x in dic:
                        setattr(self, x, dic[x])

        for x in os.listdir(".."):
            if x.endswith(".pon"):
                os.remove("../%s" % x)
                self.x_translator = x[:2]
        self.releeTRA()

        TrListas.ponPiecesLNG(self.x_pgn_english or self.translator() == "en")

        self.tutor = self.buscaTutor(self.x_tutor_clave)
        if self.tutor.clave != self.x_tutor_clave:
            self.x_tutor_clave = self.tutor.clave

    def get_last_database(self):
        dic = self.leeVariables("DATABASE")
        return dic.get("LAST_DATABASE", "")

    def set_last_database(self, last_database):
        dic = self.leeVariables("DATABASE")
        dic["LAST_DATABASE"] = last_database
        self.escVariables("DATABASE", dic)

    def get_favoritos(self):
        if self.li_favoritos is None:
            file = os.path.join(self.carpeta_config, "Favoritos.pkd")
            lista = Util.restore_pickle(file)
            if lista is None:
                lista = []
            self.li_favoritos = lista
        return self.li_favoritos

    def save_favoritos(self, lista):
        self.li_favoritos = lista
        file = os.path.join(self.carpeta_config, "Favoritos.pkd")
        Util.save_pickle(file, lista)

    def releeTRA(self):
        Translate.install(self.x_translator)

    def eloActivo(self):
        return self.x_elo

    def miceloActivo(self):
        return self.x_michelo

    def ficsActivo(self):
        return self.x_fics

    def fideActivo(self):
        return self.x_fide

    def lichessActivo(self):
        return self.x_lichess

    def ponEloActivo(self, elo):
        self.x_elo = elo

    def ponMiceloActivo(self, elo):
        self.x_michelo = elo

    def ponFicsActivo(self, elo):
        self.x_fics = elo

    def ponFideActivo(self, elo):
        self.x_fide = elo

    def ponLichessActivo(self, elo):
        self.x_lichess = elo

    def list_translations(self):
        li = []
        dlang = Code.path_resource("Locale")
        for uno in Util.listdir(dlang):
            fini = os.path.join(dlang, uno.name, "lang.ini")
            if os.path.isfile(fini):
                dic = Util.ini_dic(fini)
                li.append((uno.name, dic["NAME"], int(dic["%"]), dic["AUTHOR"]))
        li = sorted(li, key=lambda lng: lng[0])
        return li

    def listaMotoresInternos(self):
        li = [cm for k, cm in self.dic_engines.items() if not cm.siExterno]
        li = sorted(li, key=lambda cm: cm.name)
        return li

    def lista_motores_externos(self):
        li = [cm for k, cm in self.dic_engines.items() if cm.siExterno]
        li = sorted(li, key=lambda cm: cm.name)
        return li

    def lee_motores_externos(self):
        li = Util.restore_pickle(self.file_external_engines())
        if li:
            from Code.Engines import Engines

            for x in li:
                eng = Engines.Engine()
                eng.restore(x)
                clave = eng.clave
                n = 0
                while eng.clave in self.dic_engines:
                    n += 1
                    eng.clave = "%s-%d" % (clave, n)
                eng.set_extern()
                self.dic_engines[eng.clave] = eng

    def list_engines(self, si_externos=True):
        li = []
        for k, v in self.dic_engines.items():
            name = v.name
            if v.siExterno:
                if not si_externos:
                    continue
                name += " *"
            li.append((name, v.autor, v.url))
        li = sorted(li, key=operator.itemgetter(0))
        return li

    def dict_engines_fixed_elo(self):
        return OSEngines.dict_engines_fixed_elo(self.folder_internal_engines)

    def carpetaTemporal(self):
        dirTmp = os.path.join(self.carpeta, "tmp")
        Util.create_folder(dirTmp)
        return dirTmp

    def ficheroTemporal(self, extension):
        dirTmp = os.path.join(self.carpeta, "tmp")
        return Util.temporary_file(dirTmp, extension)

    def limpiaTemporal(self):
        try:
            dirTmp = os.path.join(self.carpeta, "tmp")
            for entry in Util.listdir(dirTmp):
                Util.remove_file(entry.path)
        except:
            pass

    def leeVariables(self, nomVar):
        db = UtilSQL.DictSQL(self.ficheroVariables)
        resp = db[nomVar]
        db.close()
        return resp if resp else {}

        # "DicMicElos": _("Tourney-Elo")
        # "ENG_GESTORSOLO": _("Create your own game")
        # "FICH_GESTORSOLO": _("Create your own game")
        # "ENG_VARIANTES": _("Variations") _("Edition")
        # "TRANSSIBERIAN": _("Transsiberian Railway")
        # "STSFORMULA": _("Formula to calculate elo") -  _("STS: Strategic Test Suite")
        # "PantallaColores": _("Colors")
        # "PCOLORES": _("Colors")
        # "manual_save": _("Save positions to FNS/PGN")
        # "FOLDER_ENGINES": _("External engines")
        # "MICELO":
        # "MICPER":
        # "SAVEPGN":
        # "STSRUN":
        # "crear_torneo":
        # "PARAMPELICULA":
        # "BLINDFOLD":
        # "WBG_MOVES":
        # "DBSUMMARY":
        # "DATABASE"

    def escVariables(self, nomVar, dicValores):
        db = UtilSQL.DictSQL(self.ficheroVariables)
        db[nomVar] = dicValores
        db.close()

    def leeConfTableros(self):
        db = UtilSQL.DictSQL(self.ficheroConfTableros)
        self.dic_conf_boards_pk = db.as_dictionary()
        if not ("BASE" in self.dic_conf_boards_pk):
            with open(Code.path_resource("IntFiles", "basepk.board"), "rb") as f:
                var = pickle.loads(f.read())
                db["BASE"] = self.dic_conf_boards_pk["BASE"] = var
        # with open("../resources/IntFiles/base.board", "wb") as f:
        #      f.write(pickle.dumps(db["BASE"]))
        db.close()

    def resetConfTablero(self, clave, tamDef):
        db = UtilSQL.DictSQL(self.ficheroConfTableros)
        del db[clave]
        db.close()
        self.leeConfTableros()
        return self.config_board(clave, tamDef)

    def cambiaConfTablero(self, config_board):
        xid = config_board._id
        if xid:
            db = UtilSQL.DictSQL(self.ficheroConfTableros)
            self.dic_conf_boards_pk[xid] = db[xid] = config_board.graba()
            db.close()
            self.leeConfTableros()

    def config_board(self, xid, tamDef, padre="BASE"):
        if xid == "BASE":
            ct = ConfBoards.ConfigTablero(xid, tamDef)
        else:
            ct = ConfBoards.ConfigTablero(xid, tamDef, padre=padre)
            ct.anchoPieza(tamDef)

        if xid in self.dic_conf_boards_pk:
            ct.lee(self.dic_conf_boards_pk[xid])
        else:
            db = UtilSQL.DictSQL(self.ficheroConfTableros)
            self.dic_conf_boards_pk[xid] = db[xid] = ct.graba()
            db.close()

        ct._anchoPiezaDef = tamDef

        return ct

    def save_video(self, clave, dic):
        db = UtilSQL.DictSQL(self.file_video())
        db[clave] = dic
        db.close()

    def restore_video(self, clave):
        db = UtilSQL.DictSQL(self.file_video())
        dic = db[clave]
        db.close()
        return dic