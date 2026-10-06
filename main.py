"""Flappy Bird para Android (Kivy).

Port do flappy.py original (pygame). As regras estão em logica.py; aqui ficam
só a tela, o toque e o ciclo de vida do app no Android.

Controles:
  - toque na tela (ou ESPAÇO no PC) ........ pular / começar
  - botão Voltar do Android (ou ESC no PC) .. voltar ao menu / sair
"""
import os
import time

from kivy.config import Config
from kivy.utils import platform

from logica import ALTURA, ESPACO_CANOS, FPS, LARGURA, X_PASSARO, Partida

# Precisa vir antes de importar a Window.
Config.set("kivy", "exit_on_escape", "0")  # o ESC/Voltar é tratado por nós
if platform not in ("android", "ios"):
    Config.set("graphics", "width", str(LARGURA))
    Config.set("graphics", "height", str(ALTURA))

from kivy.app import App  # noqa: E402
from kivy.clock import Clock  # noqa: E402
from kivy.core.image import Image as CoreImage  # noqa: E402
from kivy.core.text import Label as CoreLabel  # noqa: E402
from kivy.core.window import Window  # noqa: E402
from kivy.graphics import Color, Ellipse, Line, Rectangle  # noqa: E402
from kivy.uix.widget import Widget  # noqa: E402

PASTA = os.path.dirname(os.path.abspath(__file__))

# Cores (0 a 1)
PRETO = (0, 0, 0, 1)
VERDE = (0, 200 / 255, 0, 1)
AMARELO = (1, 1, 0, 1)
BRANCO = (1, 1, 1, 1)

PASSO = 1.0 / FPS
TECLA_ESPACO = 32
TECLA_VOLTAR = 27  # ESC no PC e botão Voltar no Android


class FlappyWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.estado = "menu"  # "menu", "jogando" ou "pausado"
        self.partida = None
        self.ultimo = None  # pontuação da última partida
        self.entrou_no_menu = time.monotonic()
        self.acumulado = 0.0
        self.sujo = True  # precisa redesenhar?
        self._textos = {}
        self._sprite = self._carregar_sprite()

        self.bind(size=self._marcar_sujo, pos=self._marcar_sujo)
        Clock.schedule_interval(self.tick, 1 / 60.0)

    # ---------------------------------------------------------- recursos
    @staticmethod
    def _carregar_sprite():
        try:
            textura = CoreImage(os.path.join(PASTA, "passaro.png")).texture
            textura.mag_filter = "nearest"  # mantém a pixel art nítida
            textura.min_filter = "nearest"
            return textura
        except Exception:
            return None

    def _marcar_sujo(self, *_):
        self.sujo = True

    # ----------------------------------------------------------- estados
    def iniciar(self):
        self.partida = Partida()
        self.estado = "jogando"
        self.acumulado = 0.0
        self.sujo = True

    def ir_para_menu(self):
        if self.partida is not None:
            self.ultimo = self.partida.pontos
        self.partida = None
        self.estado = "menu"
        self.entrou_no_menu = time.monotonic()
        self.sujo = True

    def pausar(self):
        if self.estado == "jogando":
            self.estado = "pausado"
            self.sujo = True

    def acao(self):
        """Toque na tela ou ESPAÇO."""
        if self.estado == "jogando":
            self.partida.pular()
        elif self.estado == "pausado":
            self.estado = "jogando"
            self.acumulado = 0.0
            self.sujo = True
        # Pequena trava no menu: evita recomeçar sem querer com o mesmo toque
        # que acabou de causar a derrota.
        elif time.monotonic() - self.entrou_no_menu > 0.6:
            self.iniciar()

    def on_touch_down(self, touch):
        self.acao()
        return True

    def tecla(self, janela, tecla, *args):
        if tecla == TECLA_ESPACO:
            self.acao()
            return True
        if tecla == TECLA_VOLTAR:
            if self.estado in ("jogando", "pausado"):
                self.ir_para_menu()
            else:
                App.get_running_app().stop()
            return True
        return False

    # ------------------------------------------------------------- laço
    def tick(self, dt):
        if self.estado == "jogando":
            # A lógica roda em passos fixos de 1/30 s, como no original,
            # independente da taxa de quadros do aparelho.
            self.acumulado += min(dt, 0.25)
            passos = 0
            while self.acumulado >= PASSO and passos < 5:
                self.partida.passo()
                self.acumulado -= PASSO
                passos += 1
                self.sujo = True
                if self.partida.terminou:
                    self.ir_para_menu()
                    break
            if self.acumulado >= PASSO:  # aparelho muito lento: descarta o atraso
                self.acumulado = 0.0

        if self.sujo:
            self.sujo = False
            self.desenhar()

    # ----------------------------------------------------------- desenho
    def _textura_texto(self, msg, cor, tamanho_px):
        chave = (msg, cor, tamanho_px)
        textura = self._textos.get(chave)
        if textura is None:
            rotulo = CoreLabel(text=msg, font_size=tamanho_px, color=cor)
            rotulo.refresh()
            textura = rotulo.texture
            if len(self._textos) > 80:
                self._textos.clear()
            self._textos[chave] = textura
        return textura

    def desenhar(self):
        esc = min(self.width / LARGURA, self.height / ALTURA)
        if esc <= 0:
            return
        # Canto do mundo virtual (500x600) centralizado na tela
        ox = self.x + (self.width - LARGURA * esc) / 2
        oy = self.y + (self.height - ALTURA * esc) / 2

        def px(x):
            return ox + x * esc

        def py(y):  # no mundo virtual o Y cresce para baixo; no Kivy, para cima
            return oy + (ALTURA - y) * esc

        def texto(msg, cor, tamanho, y_topo, x_centro=LARGURA / 2, esquerda=False):
            textura = self._textura_texto(msg, cor, max(8, round(tamanho * esc)))
            w, h = textura.size
            x = px(x_centro) if esquerda else px(x_centro) - w / 2
            Color(1, 1, 1, 1)
            Rectangle(texture=textura, pos=(x, py(y_topo) - h), size=(w, h))

        self.canvas.clear()
        with self.canvas:
            Color(*PRETO)
            Rectangle(pos=self.pos, size=self.size)

            if self.estado == "menu":
                if self._sprite is not None:
                    w, h = 150 * esc, 106 * esc
                    Color(1, 1, 1, 1)
                    Rectangle(texture=self._sprite, size=(w, h),
                              pos=(px(LARGURA / 2) - w / 2, py(70) - h))
                texto("FLAPPY BIRD", AMARELO, 44, 195)
                texto("Toque para jogar", BRANCO, 30, 260)
                if self.ultimo is not None:
                    texto(f"Última pontuação: {self.ultimo}", BRANCO, 30, 305)
            else:
                self._desenhar_partida(esc, px, py)
                texto(f"Pontos: {self.partida.pontos}", BRANCO, 30, 10,
                      x_centro=10, esquerda=True)
                if self.estado == "pausado":
                    Color(0, 0, 0, 0.7)
                    Rectangle(pos=(ox, oy), size=(LARGURA * esc, ALTURA * esc))
                    texto("PAUSADO", AMARELO, 44, 230)
                    texto("Toque para continuar", BRANCO, 30, 290)

            # Faixas pretas nas sobras da tela (nada vaza para fora do mundo)
            Color(*PRETO)
            direita = ox + LARGURA * esc
            topo = oy + ALTURA * esc
            Rectangle(pos=(self.x, self.y), size=(max(0, ox - self.x), self.height))
            Rectangle(pos=(direita, self.y), size=(max(0, self.right - direita), self.height))
            Rectangle(pos=(self.x, self.y), size=(self.width, max(0, oy - self.y)))
            Rectangle(pos=(self.x, topo), size=(self.width, max(0, self.top - topo)))

    def _desenhar_partida(self, esc, px, py):
        espessura = max(1.0, 6 * esc)
        Color(*VERDE)
        for cano in self.partida.canos:
            x = cano["x"]
            topo = cano["topo"]
            baixo = topo + ESPACO_CANOS
            # Cano superior
            Line(points=[px(x), py(0), px(x), py(topo)], width=espessura, cap="none")
            Line(points=[px(x - 20), py(topo), px(x + 20), py(topo)],
                 width=espessura, cap="none")
            # Cano inferior
            Line(points=[px(x), py(baixo), px(x), py(ALTURA)], width=espessura, cap="none")
            Line(points=[px(x - 20), py(baixo), px(x + 20), py(baixo)],
                 width=espessura, cap="none")

        # Pássaro (ponto amarelo, como no original)
        raio = 6 * esc
        Color(*AMARELO)
        Ellipse(pos=(px(X_PASSARO) - raio, py(self.partida.y) - raio),
                size=(2 * raio, 2 * raio))


class FlappyApp(App):
    title = "Flappy Bird"
    icon = os.path.join(PASTA, "icon.png")  # ícone da janela no PC

    def build(self):
        Window.clearcolor = PRETO
        self.jogo = FlappyWidget()
        Window.bind(on_keyboard=self.jogo.tecla)
        return self.jogo

    def on_pause(self):
        # Android: app foi para segundo plano. Pausa a partida e mantém o app vivo.
        self.jogo.pausar()
        return True

    def on_resume(self):
        self.jogo.sujo = True


if __name__ == "__main__":
    FlappyApp().run()
