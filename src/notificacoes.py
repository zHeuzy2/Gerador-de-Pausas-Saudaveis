"""Notificações sonoras e visuais ao trocar de ciclo.

Mantém tudo na biblioteca padrão. No Windows usa ``winsound``; em outros
sistemas faz fallback para o "bell" do terminal. Falhas de áudio nunca
interrompem o app.
"""

from __future__ import annotations

import sys


def tocar_som(modo: str) -> None:
    """Toca um som curto ao trocar de ciclo. ``modo`` é 'foco' ou 'pausa'."""
    try:
        if sys.platform == "win32":
            import winsound

            # Frequências diferentes para distinguir os modos.
            frequencia = 660 if modo == "pausa" else 440
            winsound.Beep(frequencia, 250)
        else:
            # Fallback portátil: bell do terminal.
            print("\a", end="", flush=True)
    except Exception:
        # Áudio é opcional; nunca deve quebrar o fluxo do timer.
        pass


def notificar_sistema(titulo: str, mensagem: str) -> None:
    """Exibe uma notificação do sistema, se houver suporte disponível.

    Tenta usar a biblioteca opcional ``plyer``; se não estiver instalada,
    silenciosamente ignora (o app continua funcionando com o som + a UI).
    """
    try:
        from plyer import notification

        notification.notify(title=titulo, message=mensagem, timeout=5)
    except Exception:
        pass
