"""Lógica de contagem regressiva do timer (equivalente ao useTimer.js do plano).

Mantém o estado do tempo e expõe métodos para iniciar, pausar, retomar e
resetar. A contagem em si (o "tick" a cada segundo) é controlada pela camada
de interface (Tkinter) através do método ``tick``, evitando threads e
garantindo que não haja "vazamento" de intervalos.
"""

from __future__ import annotations


class Timer:
    """Contagem regressiva simples baseada em segundos restantes."""

    def __init__(self, segundos: int) -> None:
        self.duracao = segundos
        self.restante = segundos
        self.rodando = False

    def iniciar(self) -> None:
        self.rodando = True

    def pausar(self) -> None:
        self.rodando = False

    def retomar(self) -> None:
        if self.restante > 0:
            self.rodando = True

    def resetar(self, segundos: int | None = None) -> None:
        if segundos is not None:
            self.duracao = segundos
        self.restante = self.duracao
        self.rodando = False

    def definir_duracao(self, segundos: int) -> None:
        """Atualiza a duração total e reinicia o tempo restante."""
        self.duracao = segundos
        self.restante = segundos

    def tick(self) -> bool:
        """Desconta um segundo. Retorna True quando o tempo chega a zero."""
        if not self.rodando:
            return False
        if self.restante > 0:
            self.restante -= 1
        if self.restante <= 0:
            self.restante = 0
            self.rodando = False
            return True
        return False

    @property
    def terminado(self) -> bool:
        return self.restante <= 0

    def formatado(self) -> str:
        """Devolve o tempo restante no formato MM:SS."""
        minutos, segundos = divmod(max(self.restante, 0), 60)
        return f"{minutos:02d}:{segundos:02d}"
