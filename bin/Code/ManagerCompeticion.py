from Code.Openings import Opening
from Code.Polyglots import Books
from Code import Manager
from Code.Base import Move
from Code.QT import QTUtil2
from Code import Tutor
from Code import Adjourns
from Code import CompetitionWithTutor
import Code
from Code.Engines import EngineResponse
from Code.Base.Constantes import *


class ManagerCompeticion(Manager.Manager):
    def inicio(self, categorias, categoria, nivel, is_white, puntos):
        self.base_inicio(categorias, categoria, nivel, is_white, puntos)
        self.siguiente_jugada()

    def base_inicio(self, categorias, categoria, nivel, is_white, puntos):
        self.game_type = GT_COMPETITION_WITH_TUTOR

        self.liReiniciar = categoria, nivel, is_white

        self.dbm = CompetitionWithTutor.DBManagerCWT()

        self.resultado = None
        self.human_is_playing = False
        self.state = ST_PLAYING

        self.is_competitive = True

        self.plays_instead_of_me_option = True

        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.rm_rival = None

        self.categorias = categorias
        self.categoria = categoria
        self.nivelJugado = nivel
        self.puntos = puntos

        self.is_tutor_enabled = (Code.dgtDispatch is None) and self.configuration.x_default_tutor_active
        self.main_window.set_activate_tutor(self.is_tutor_enabled)
        self.tutor_book = Books.BookGame(Code.tbook)

        self.ayudas = categoria.ayudas
        self.ayudas_iniciales = self.ayudas  # Se guarda para guardar el PGN

        self.in_the_opening = True
        self.opening = Opening.OpeningPol(nivel)  # lee las aperturas

        self.rival_conf = self.dbm.get_current_rival()
        self.xrival = self.procesador.creaManagerMotor(self.rival_conf, None, nivel)

        self.main_window.pon_toolbar(
            (TB_CANCEL, TB_RESIGN, TB_TAKEBACK, TB_REINIT, TB_ADJOURN, TB_CONFIG, TB_UTILITIES)
        )
        self.main_window.activaJuego(True, False)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.ponPiezasAbajo(is_white)
        self.ponAyudas(self.ayudas)
        self.show_side_indicator(True)
        label = "%s: <b>%s</b><br>%s %s %d" % (_("Opponent"), self.xrival.name, categoria.name(), _("Level"), nivel)
        if self.puntos:
            label += " (+%d %s)" % (self.puntos, _("points"))
        self.set_label1(label)
        self.xrotulo2()

        self.pgnRefresh(True)
        self.ponCapInfoPorDefecto()

        self.game.add_tag("Event", _("Competition with tutor"))

        player = self.configuration.nom_player()
        other = "%s (%s %d)" % (self.xrival.name, _("Level"), self.nivelJugado)
        w, b = (player, other) if self.is_human_side_white else (other, player)
        self.game.add_tag("White", w)
        self.game.add_tag("Black", b)

        self.is_analyzed_by_tutor = False

        self.check_boards_setposition()

    def xrotulo2(self):
        self.set_label2(
            "%s: <b>%s</b><br>%s: %d %s"
            % (_("Tutor"), self.xtutor.name, _("Total score"), self.dbm.puntuacion(), _("pts"))
        )

    def run_action(self, key):

        if key == TB_CANCEL:
            self.finalizar()

        elif key == TB_RESIGN:
            self.rendirse()

        elif key == TB_TAKEBACK:
            self.atras()

        elif key == TB_REINIT:
            self.reiniciar()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True, siCambioTutor=True)

        elif key == TB_UTILITIES:
            self.utilidades(siArbol=False)

        elif key == TB_ADJOURN:
            self.adjourn()

        else:
            self.rutinaAccionDef(key)

    def reiniciar(self):
        if len(self.game) and QTUtil2.pregunta(self.main_window, _("Restart the game?")):
            self.game.set_position()
            categoria, nivel, is_white = self.liReiniciar
            self.inicio(self.categorias, categoria, nivel, is_white, self.puntos)

    def adjourn(self):
        if len(self.game) and QTUtil2.pregunta(self.main_window, _("Do you want to adjourn the game?")):

            label_menu = _("Competition with tutor") + ". " + self.xrival.name

            dic = {
                "ISWHITE": self.is_human_side_white,
                "GAME_SAVE": self.game.save(),
                "SITUTOR": self.is_tutor_enabled,
                "AYUDAS": self.ayudas,
                "CATEGORIA": self.categoria.key,
                "LEVEL": self.nivelJugado,
                "PUNTOS": self.puntos,
                "RIVAL_KEY": self.dbm.get_current_rival_key(),
            }

            with Adjourns.Adjourns() as adj:
                adj.add(self.game_type, dic, label_menu)
                adj.si_seguimos(self)

    def run_adjourn(self, dic):
        puntos = dic["PUNTOS"]
        is_white = dic["ISWHITE"]
        nivel = dic["LEVEL"]
        dbm = CompetitionWithTutor.DBManagerCWT()
        categorias = dbm.get_categorias_rival(dic["RIVAL_KEY"])
        categoria = categorias.segun_clave(dic["CATEGORIA"])
        self.base_inicio(categorias, categoria, nivel, is_white, puntos)
        self.game.restore(dic["GAME_SAVE"])
        self.goto_end()

        self.siguiente_jugada()

    def final_x(self):
        return self.finalizar()

    def finalizar(self):
        if self.state == ST_ENDGAME:
            self.ponFinJuego()
            return True
        siJugadas = len(self.game) > 0
        if siJugadas:
            if not QTUtil2.pregunta(self.main_window, _("End game?")):
                return False  # no termina
            self.guardarNoTerminados()
            self.ponFinJuego()
        else:
            self.procesador.inicio()

        return False

    def rendirse(self):
        if self.state == ST_ENDGAME:
            return True
        siJugadas = len(self.game) > 0
        if siJugadas:
            if not QTUtil2.pregunta(self.main_window, _("Do you want to resign?")):
                return False  # no abandona
            self.resultado = RS_WIN_OPPONENT
            self.game.resign(self.is_human_side_white)
            self.guardarGanados(False)
            self.ponFinJuego()
        else:
            self.procesador.inicio()

        return False

    def atras(self):
        if self.ayudas and len(self.game):
            if QTUtil2.pregunta(self.main_window, _("Do you want to go back in the last movement?")):
                self.ayudas -= 1
                self.ponAyudas(self.ayudas)
                self.game.anulaUltimoMovimiento(self.is_human_side_white)
                self.in_the_opening = False
                self.game.assign_opening()
                self.goto_end()
                self.is_analyzed_by_tutor = False
                self.refresh()
                self.siguiente_jugada()

    def siguiente_jugada(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()
        is_white = self.game.last_position.is_white

        if self.game.is_finished():
            self.muestra_resultado()
            return

        if self.ayudas == 0:
            if self.categoria.sinAyudasFinal:
                self.quitaAyudas()
                self.is_tutor_enabled = False

        siRival = is_white == self.is_engine_side_white
        self.set_side_indicator(is_white)

        self.refresh()

        if siRival:
            self.pensando(True)
            self.disable_all()

            siPensar = True

            if self.in_the_opening:

                siBien, from_sq, to_sq, promotion = self.opening.run_engine(self.fenUltimo())

                if siBien:
                    self.rm_rival = EngineResponse.EngineResponse("Opening", self.is_engine_side_white)
                    self.rm_rival.from_sq = from_sq
                    self.rm_rival.to_sq = to_sq
                    self.rm_rival.promotion = promotion
                    siPensar = False
                else:
                    self.in_the_opening = False

            if siPensar:
                self.rm_rival = self.xrival.juega()

            self.pensando(False)

            if self.mueve_rival(self.rm_rival):
                self.siguiente_jugada()
        else:
            self.human_is_playing = True
            self.activate_side(is_white)
            self.analizaInicio()

    def muestra_resultado(self):
        self.state = ST_ENDGAME
        self.disable_all()
        self.human_is_playing = False

        mensaje, beep, player_win = self.game.label_resultado_player(self.is_human_side_white)
        self.beepResultado(beep)
        if player_win:
            hecho = "B" if self.is_human_side_white else "N"
            if self.categorias.put_result(self.categoria, self.nivelJugado, hecho):
                mensaje += "<br><br>%s: %d (%s)" % (
                    _("Move to the next level"),
                    self.categoria.level_done + 1,
                    self.categoria.name(),
                )
            self.dbm.set_categorias_rival(self.rival_conf.key, self.categorias)
            if self.puntos:
                puntuacion = self.dbm.puntuacion()
                mensaje += "<br><br>%s: %d+%d = %d %s" % (
                    _("Total score"),
                    puntuacion - self.puntos,
                    self.puntos,
                    puntuacion,
                    _("pts"),
                )
                self.xrotulo2()

        self.guardarGanados(player_win)
        self.mensaje(mensaje)
        self.ponFinJuego()

    def analizaInicio(self):
        self.siAnalizando = False
        self.is_analyzed_by_tutor = False
        if self.is_tutor_enabled:
            self.is_analyzed_by_tutor = False
            if self.continueTt:
                if not self.is_finished():
                    self.siAnalizando = True
                    self.xtutor.ac_inicio(self.game)
            else:
                self.mrmTutor = self.analizaTutor()
                self.is_analyzed_by_tutor = True

    def analizaFinal(self):
        if self.siAnalizando:
            self.mrmTutor = self.xtutor.ac_final(-1)
            self.is_analyzed_by_tutor = True
            self.siAnalizando = False

    def cambiaActivarTutor(self):
        self.is_tutor_enabled = not self.is_tutor_enabled
        self.set_activate_tutor(self.is_tutor_enabled)
        self.analizaFinal()

    def player_has_moved(self, from_sq, to_sq, promotion=None):
        move = self.checkmueve_humano(from_sq, to_sq, promotion)
        if not move:
            return False
        movimiento = move.movimiento()
        self.analizaFinal()

        siMirarTutor = self.is_tutor_enabled
        if self.in_the_opening:
            if self.opening.check_human(self.fenUltimo(), from_sq, to_sq):
                siMirarTutor = False

        if siMirarTutor:
            if not self.is_analyzed_by_tutor:
                self.mrmTutor = self.analizaTutor()

            if self.mrmTutor is None:
                self.sigueHumano()
                return False
            if not self.tutor_book.si_esta(self.fenUltimo(), movimiento):
                if self.mrmTutor.mejorMovQue(movimiento):
                    self.refresh()
                    if not move.is_mate:
                        tutor = Tutor.Tutor(self, self, move, from_sq, to_sq, False)

                        if self.in_the_opening:
                            liApPosibles = self.listaOpeningsStd.list_possible_openings(self.game)
                        else:
                            liApPosibles = None

                        if tutor.elegir(self.ayudas > 0, liApPosibles=liApPosibles):
                            if self.ayudas > 0:  # doble entrada a tutor.
                                self.set_piece_again(from_sq)
                                self.ayudas -= 1
                                from_sq = tutor.from_sq
                                to_sq = tutor.to_sq
                                promotion = tutor.promotion
                                siBien, mens, jgTutor = Move.get_game_move(
                                    self.game, self.game.last_position, from_sq, to_sq, promotion
                                )
                                if siBien:
                                    move = jgTutor
                        elif self.configuration.x_save_tutor_variations:
                            tutor.ponVariations(move, 1 + len(self.game) / 2)

                        del tutor

        self.move_the_pieces(move.liMovs)
        self.add_move(move, True)
        self.siguiente_jugada()
        return True

    def add_move(self, move, siNuestra):
        self.game.add_move(move)

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.ponAyudas(self.ayudas)

        self.pgnRefresh(self.game.last_position.is_white)
        self.refresh()

        self.check_boards_setposition()

    def mueve_rival(self, respMotor):
        from_sq = respMotor.from_sq
        to_sq = respMotor.to_sq

        promotion = respMotor.promotion

        siBien, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if siBien:
            self.error = ""
            self.add_move(move, False)
            self.move_the_pieces(move.liMovs, True)

            return True
        else:
            self.error = mens
            return False