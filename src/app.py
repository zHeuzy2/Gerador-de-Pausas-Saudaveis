"""Gerador de Pausas Saudáveis — aplicação desktop (CustomTkinter).

Timer estilo Pomodoro com modos de foco e pausa que alternam
automaticamente. No modo foco, exibe uma lista de tarefas com checkmark;
no modo pausa, sorteia uma sugestão saudável (alongamento, hidratação ou
respiração) vinda do sugestoes.json.
"""

from __future__ import annotations

import customtkinter as ctk

from notificacoes import notificar_sistema, tocar_som
from sugestoes import carregar_sugestoes, sortear_sugestao
from timer import Timer

# Paleta de cores por modo (foco sóbrio/concentrado, pausa leve/relaxante).
CORES = {
    "foco": {
        "fundo": "#1b2735",
        "card": "#27384d",
        "destaque": "#f1f5f9",
        "secundaria": "#93a8bd",
        "botao": "#3b82f6",
        "botao_hover": "#2563eb",
    },
    "pausa": {
        "fundo": "#0f766e",
        "card": "#0d8478",
        "destaque": "#ecfdf5",
        "secundaria": "#bdf5e6",
        "botao": "#34d399",
        "botao_hover": "#10b981",
    },
}

ROTULOS = {"foco": "Hora de focar", "pausa": "Hora da pausa"}

# Durações padrão (em minutos).
FOCO_PADRAO = 25
PAUSA_PADRAO = 5


class AppPausas(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Gerador de Pausas Saudáveis")
        self.minsize(380, 700)
        self.geometry("440x780")

        ctk.set_appearance_mode("dark")

        self.sugestoes = carregar_sugestoes()

        # Configurações de duração (minutos).
        self.min_foco = ctk.IntVar(value=FOCO_PADRAO)
        self.min_pausa = ctk.IntVar(value=PAUSA_PADRAO)

        # Estado do ciclo.
        self.modo = "foco"
        self.ciclos = 0
        self.timer = Timer(self.min_foco.get() * 60)
        self._job = None  # id do after() para limpeza correta

        # Tarefas do foco: cada item é {"texto", "feita" (BooleanVar), "linha"}.
        self.tarefas: list[dict] = []
        self.fonte_tarefa = ctk.CTkFont(size=13)
        self.fonte_tarefa_feita = ctk.CTkFont(size=13, overstrike=True)

        self._construir_ui()
        self._aplicar_tema()
        self._mostrar_vista()
        self._atualizar_display()

    # ------------------------------------------------------------------ UI
    def _construir_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Indicador de modo.
        self.lbl_modo = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.lbl_modo.grid(row=0, column=0, pady=(26, 2))

        # Contador de ciclos.
        self.lbl_ciclos = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=13))
        self.lbl_ciclos.grid(row=1, column=0, pady=(0, 4))

        # Display do tempo (elemento central, grande).
        self.lbl_tempo = ctk.CTkLabel(
            self, text="25:00", font=ctk.CTkFont(size=88, weight="bold")
        )
        self.lbl_tempo.grid(row=2, column=0, pady=8)

        # Controles.
        controles = ctk.CTkFrame(self, fg_color="transparent")
        controles.grid(row=3, column=0, pady=8)

        self.btn_iniciar = ctk.CTkButton(
            controles,
            text="▶  Iniciar",
            font=ctk.CTkFont(size=15, weight="bold"),
            width=150,
            height=46,
            corner_radius=23,
            command=self._iniciar_pausar,
        )
        self.btn_iniciar.grid(row=0, column=0, padx=8)

        self.btn_resetar = ctk.CTkButton(
            controles,
            text="↺  Resetar",
            font=ctk.CTkFont(size=15),
            width=130,
            height=46,
            corner_radius=23,
            fg_color="transparent",
            border_width=2,
            command=self._resetar,
        )
        self.btn_resetar.grid(row=0, column=1, padx=8)

        # ---- Vista de sugestão (modo pausa) --------------------------------
        self.vista_sugestao = ctk.CTkFrame(self, corner_radius=18)
        self.vista_sugestao.grid_columnconfigure(0, weight=1)

        self.lbl_card_icon = ctk.CTkLabel(
            self.vista_sugestao, text="🌿", font=ctk.CTkFont(size=46)
        )
        self.lbl_card_icon.grid(row=0, column=0, pady=(18, 2))
        self.lbl_card_titulo = ctk.CTkLabel(
            self.vista_sugestao, text="", font=ctk.CTkFont(size=17, weight="bold")
        )
        self.lbl_card_titulo.grid(row=1, column=0, pady=2)
        self.lbl_card_desc = ctk.CTkLabel(
            self.vista_sugestao,
            text="",
            font=ctk.CTkFont(size=13),
            wraplength=320,
            justify="center",
        )
        self.lbl_card_desc.grid(row=2, column=0, pady=(2, 20), padx=14)

        # ---- Vista de tarefas (modo foco) ----------------------------------
        self.vista_tarefas = ctk.CTkFrame(self, corner_radius=18)
        self.vista_tarefas.grid_columnconfigure(0, weight=1)
        self.vista_tarefas.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self.vista_tarefas,
            text="🎯  Tarefas do foco",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, pady=(14, 8), padx=14, sticky="w")

        entrada = ctk.CTkFrame(self.vista_tarefas, fg_color="transparent")
        entrada.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")
        entrada.grid_columnconfigure(0, weight=1)

        self.entry_tarefa = ctk.CTkEntry(
            entrada, placeholder_text="Adicionar uma tarefa..."
        )
        self.entry_tarefa.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_tarefa.bind("<Return>", lambda _e: self._adicionar_tarefa())

        self.btn_add_tarefa = ctk.CTkButton(
            entrada, text="+", width=40, font=ctk.CTkFont(size=18, weight="bold"),
            command=self._adicionar_tarefa,
        )
        self.btn_add_tarefa.grid(row=0, column=1)

        self.lista_tarefas = ctk.CTkScrollableFrame(
            self.vista_tarefas, fg_color="transparent", height=150
        )
        self.lista_tarefas.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.lista_tarefas.grid_columnconfigure(0, weight=1)

        self.lbl_tarefas_vazio = ctk.CTkLabel(
            self.lista_tarefas,
            text="Nenhuma tarefa ainda.\nAdicione o que pretende fazer neste foco.",
            font=ctk.CTkFont(size=12),
            justify="center",
        )

        # Configurações de duração.
        config = ctk.CTkFrame(self, fg_color="transparent")
        config.grid(row=5, column=0, pady=(4, 20))

        ctk.CTkLabel(config, text="Foco (min)", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, padx=(0, 8)
        )
        self.spin_foco = ctk.CTkOptionMenu(
            config,
            width=78,
            values=[str(v) for v in (15, 20, 25, 30, 45, 50, 60)],
            variable=ctk.StringVar(value=str(FOCO_PADRAO)),
            command=lambda v: self._set_duracao("foco", v),
        )
        self.spin_foco.grid(row=0, column=1, padx=(0, 24))

        ctk.CTkLabel(config, text="Pausa (min)", font=ctk.CTkFont(size=12)).grid(
            row=0, column=2, padx=(0, 8)
        )
        self.spin_pausa = ctk.CTkOptionMenu(
            config,
            width=78,
            values=[str(v) for v in (3, 5, 10, 15, 20)],
            variable=ctk.StringVar(value=str(PAUSA_PADRAO)),
            command=lambda v: self._set_duracao("pausa", v),
        )
        self.spin_pausa.grid(row=0, column=3)

    # --------------------------------------------------------------- tema
    def _aplicar_tema(self) -> None:
        c = CORES[self.modo]
        self.configure(fg_color=c["fundo"])

        self.lbl_modo.configure(text_color=c["destaque"])
        self.lbl_ciclos.configure(text_color=c["secundaria"])
        self.lbl_tempo.configure(text_color=c["destaque"])

        self.vista_sugestao.configure(fg_color=c["card"])
        self.lbl_card_icon.configure(text_color=c["destaque"])
        self.lbl_card_titulo.configure(text_color=c["destaque"])
        self.lbl_card_desc.configure(text_color=c["secundaria"])

        self.btn_iniciar.configure(fg_color=c["botao"], hover_color=c["botao_hover"])
        self.btn_resetar.configure(
            border_color=c["botao"], text_color=c["destaque"], hover_color=c["card"]
        )

    # ----------------------------------------------------------- tarefas
    def _adicionar_tarefa(self) -> None:
        texto = self.entry_tarefa.get().strip()
        if not texto:
            return
        self.entry_tarefa.delete(0, "end")

        cf = CORES["foco"]
        linha = ctk.CTkFrame(self.lista_tarefas, fg_color="transparent")

        var = ctk.BooleanVar(value=False)
        chk = ctk.CTkCheckBox(
            linha,
            text=texto,
            variable=var,
            font=self.fonte_tarefa,
            fg_color=cf["botao"],
            hover_color=cf["botao_hover"],
            text_color=cf["destaque"],
        )
        chk.grid(row=0, column=0, sticky="w", padx=(2, 6), pady=2)
        linha.grid_columnconfigure(0, weight=1)

        item = {"texto": texto, "feita": var, "linha": linha, "chk": chk}
        chk.configure(command=lambda it=item: self._alternar_tarefa(it))

        btn_del = ctk.CTkButton(
            linha,
            text="✕",
            width=28,
            height=24,
            fg_color="transparent",
            hover_color=cf["card"],
            text_color=cf["secundaria"],
            command=lambda it=item: self._remover_tarefa(it),
        )
        btn_del.grid(row=0, column=1, sticky="e")

        self.tarefas.append(item)
        self._reposicionar_tarefas()

    def _alternar_tarefa(self, item: dict) -> None:
        feita = item["feita"].get()
        cf = CORES["foco"]
        item["chk"].configure(
            font=self.fonte_tarefa_feita if feita else self.fonte_tarefa,
            text_color=cf["secundaria"] if feita else cf["destaque"],
        )

    def _remover_tarefa(self, item: dict) -> None:
        item["linha"].destroy()
        self.tarefas.remove(item)
        self._reposicionar_tarefas()

    def _reposicionar_tarefas(self) -> None:
        """Reorganiza as linhas e mostra/esconde o estado vazio."""
        if self.tarefas:
            self.lbl_tarefas_vazio.grid_forget()
            for i, item in enumerate(self.tarefas):
                item["linha"].grid(row=i, column=0, sticky="ew", pady=1)
        else:
            self.lbl_tarefas_vazio.grid(row=0, column=0, pady=24)

    # ------------------------------------------------------------- vistas
    def _mostrar_vista(self) -> None:
        """Alterna entre a lista de tarefas (foco) e o card de sugestão (pausa)."""
        if self.modo == "foco":
            self.vista_sugestao.grid_forget()
            self.vista_tarefas.grid(row=4, column=0, padx=28, pady=20, sticky="nsew")
            self._reposicionar_tarefas()
        else:
            self.vista_tarefas.grid_forget()
            self.vista_sugestao.grid(row=4, column=0, padx=28, pady=20, sticky="ew")

    # --------------------------------------------------------- callbacks
    def _set_duracao(self, modo: str, valor: str) -> None:
        minutos = max(1, int(valor))
        if modo == "foco":
            self.min_foco.set(minutos)
        else:
            self.min_pausa.set(minutos)
        if not self.timer.rodando and self.modo == modo:
            self.timer.definir_duracao(minutos * 60)
            self._atualizar_display()

    def _duracao_atual(self) -> int:
        minutos = self.min_foco.get() if self.modo == "foco" else self.min_pausa.get()
        return max(1, int(minutos)) * 60

    def _iniciar_pausar(self) -> None:
        if self.timer.rodando:
            self.timer.pausar()
            self.btn_iniciar.configure(text="▶  Retomar")
            self._cancelar_loop()
        else:
            if self.timer.terminado:
                self.timer.resetar(self._duracao_atual())
            self.timer.iniciar()
            self.btn_iniciar.configure(text="⏸  Pausar")
            self._loop()

    def _resetar(self) -> None:
        self._cancelar_loop()
        self.modo = "foco"
        self.ciclos = 0
        self.timer.resetar(self.min_foco.get() * 60)
        self.btn_iniciar.configure(text="▶  Iniciar")
        self._aplicar_tema()
        self._mostrar_vista()
        self._atualizar_display()

    # -------------------------------------------------------------- loop
    def _loop(self) -> None:
        """Tick a cada 1s usando after() — limpo no _cancelar_loop()."""
        terminou = self.timer.tick()
        self._atualizar_display()
        if terminou:
            self._trocar_modo()
            return
        self._job = self.after(1000, self._loop)

    def _cancelar_loop(self) -> None:
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None

    def _trocar_modo(self) -> None:
        self._cancelar_loop()

        if self.modo == "foco":
            self.ciclos += 1
            self.modo = "pausa"
            self.timer.resetar(self.min_pausa.get() * 60)
            self._mostrar_sugestao()
            tocar_som("pausa")
            notificar_sistema("Hora da pausa!", "Que tal uma pausa saudável?")
        else:
            self.modo = "foco"
            self.timer.resetar(self.min_foco.get() * 60)
            tocar_som("foco")
            notificar_sistema("De volta ao foco!", "Bom trabalho. Hora de focar.")

        self._aplicar_tema()
        self._mostrar_vista()
        self._atualizar_display()

        # Alterna automaticamente: já começa o próximo ciclo.
        self.timer.iniciar()
        self.btn_iniciar.configure(text="⏸  Pausar")
        self._loop()

    # ---------------------------------------------------------- displays
    def _mostrar_sugestao(self) -> None:
        s = sortear_sugestao(self.sugestoes)
        self.lbl_card_icon.configure(text=s.get("icon", "🌿"))
        self.lbl_card_titulo.configure(text=s.get("titulo", "Faça uma pausa"))
        self.lbl_card_desc.configure(text=s.get("descricao", ""))

    def _atualizar_display(self) -> None:
        self.lbl_tempo.configure(text=self.timer.formatado())
        self.lbl_modo.configure(text=ROTULOS[self.modo])
        self.lbl_ciclos.configure(text=f"Ciclos completados: {self.ciclos}")


def main() -> None:
    app = AppPausas()
    app.mainloop()


if __name__ == "__main__":
    main()
