from Code import Util
from Code.Base.Constantes import (
    ST_PLAYING,
    TB_REINIT,
    TB_TAKEBACK,
    TB_CONFIG,
    TB_ADJOURN,
    TB_CANCEL,
    TB_PAUSE,
    TB_RESIGN,
    TB_UTILITIES,
    GT_AGAINST_CHILD_ENGINE,
    WHITE,
    BLACK,
)
from Code.Openings import Opening
from Code.PlayAgainstEngine import ManagerPlayAgainstEngine
from Code.QT import Iconos


class ManagerPerson(ManagerPlayAgainstEngine.ManagerPlayAgainstEngine):
    def base_inicio(self, dic_var):
        self.reinicio = dic_var

        self.cache = dic_var.get("cache", {})

        self.game_type = GT_AGAINST_CHILD_ENGINE

        self.human_is_playing = False
        self.plays_instead_of_me_option = True
        self.state = ST_PLAYING

        self.summary = {}  # numJugada : "a"ccepted, "s"ame, "r"ejected, dif points, time used
        self.with_summary = dic_var.get("SUMMARY", False)

        is_white = dic_var["ISWHITE"]
        self.human_side = is_white
        self.is_engine_side_white = not is_white

        w, b = self.configuration.nom_player(), _F(dic_var["RIVAL"])
        if not is_white:
            w, b = b, w
        self.game.set_tag("Event", _("Opponents for young players"))
        self.game.set_tag("White", w)
        self.game.set_tag("Black", b)

        self.with_takeback = True

        cmrival = self.configuration.buscaRival("irina", None)
        self.xrival = self.procesador.creaManagerMotor(cmrival, None, 2)
        self.rival_name = dic_var["RIVAL"]
        self.xrival.set_option("Personality", self.rival_name)
        if not dic_var["FASTMOVES"]:
            self.xrival.set_option("Max Time", "5")
            self.xrival.set_option("Min Time", "1")
        self.xrival.name = _F(self.rival_name)

        self.lirm_engine = []
        self.next_test_resign = 0
        self.resign_limit = -99999  # never

        self.aperturaObl = self.aperturaStd = None

        self.human_is_playing = False
        self.state = ST_PLAYING
        self.siAnalizando = False

        self.aperturaStd = Opening.OpeningPol(1)

        self.set_dispatcher(self.player_has_moved)
        self.main_window.set_notify(self.mueve_rival_base)

        self.thinking(True)

        self.main_window.set_activate_tutor(False)

        self.hints = 0
        self.ayudas_iniciales = 0

        self.xrival.is_white = self.is_engine_side_white

        self.siTiempo = dic_var["SITIEMPO"]
        if self.siTiempo:
            self.maxSegundos = dic_var["MINUTOS"] * 60.0
            self.segundosJugada = dic_var["SEGUNDOS"]
            self.secs_extra = dic_var.get("MINEXTRA", 0) * 60.0

            self.vtime = {WHITE: Util.Timer(self.maxSegundos), BLACK: Util.Timer(self.maxSegundos)}

            time_control = "%d" % int(self.maxSegundos)
            if self.segundosJugada:
                time_control += "+%d" % self.segundosJugada
            self.game.set_tag("TimeControl", time_control)

        self.thinking(False)

        li = [TB_CANCEL, TB_RESIGN, TB_TAKEBACK, TB_REINIT, TB_ADJOURN, TB_PAUSE, TB_CONFIG, TB_UTILITIES]
        self.main_window.pon_toolbar(li)

        self.main_window.activaJuego(True, self.siTiempo)

        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.remove_hints(True, siQuitarAtras=False)
        self.put_pieces_bottom(is_white)

        imagen = getattr(Iconos, "pm%s" % self.rival_name)

        self.main_window.base.lbRotulo1.ponImagen(imagen())
        self.main_window.base.lbRotulo1.show()

        self.ponCapInfoPorDefecto()

        self.pgnRefresh(True)

        rival = self.xrival.name
        player = self.configuration.x_player
        bl, ng = player, rival
        if self.is_engine_side_white:
            bl, ng = ng, bl
        if self.siTiempo:
            tpBL = self.vtime[True].etiqueta()
            tpNG = self.vtime[False].etiqueta()
            self.main_window.ponDatosReloj(bl, tpBL, ng, tpNG)
            self.refresh()
            self.main_window.start_clock(self.set_clock, 400)
        else:
            self.main_window.base.change_player_labels(bl, ng)

        self.main_window.set_notify(self.mueve_rival_base)

        self.check_boards_setposition()

        self.game.tag_timestart()
