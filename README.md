# 🌿 Gerador de Pausas Saudáveis

> Um timer estilo Pomodoro que une produtividade e bem-estar: a cada pausa, ele sugere uma atividade saudável — alongamento, hidratação ou respiração — para você descansar de verdade.

Versão **desktop em Python** do projeto, com interface moderna feita em **CustomTkinter**, adaptada a partir do plano original pensado para a web. Roda sem back-end.

![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-green)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

## ✨ Funcionalidades

- ⏱️ Timer Pomodoro com **ciclo de foco** (padrão 25 min) e **pausa** (padrão 5 min).
- ▶️ Controles de **Iniciar**, **Pausar/Retomar** e **Resetar**.
- 🔢 Display de tempo no formato `MM:SS`, atualizando a cada segundo.
- 🔁 **Alternância automática** entre foco e pausa ao zerar o tempo.
- 🌱 A cada pausa, sorteia uma **sugestão saudável aleatória** (misturando os tipos) com ícone, título e descrição.
- ✅ No modo foco, uma **lista de tarefas** com checkmark: adicione o que pretende fazer e marque conforme conclui.
- 🔔 **Notificação** ao trocar de ciclo: som curto + notificação do sistema (quando disponível).
- 🎨 **Indicador visual** claro do modo atual (a cor de fundo muda entre foco e pausa).
- ⚙️ **Configurações** para ajustar a duração de foco e de pausa.
- 📊 **Contador de ciclos** completados na sessão.
- 🧹 Limpeza correta do loop do timer (sem "vazar" agendamentos).

## ➕ Como adicionar novas sugestões

As atividades ficam em [`src/data/sugestoes.json`](src/data/sugestoes.json), agrupadas por tipo de pausa (`alongamento`, `hidratacao`, `respiracao`). Para adicionar uma nova sugestão, basta inserir um objeto na lista do tipo desejado:

```json
{
  "alongamento": [
    {
      "titulo": "Alongue as panturrilhas",
      "descricao": "Em pé, apoie as mãos na parede e estique uma perna para trás por 20s.",
      "icon": "🦵"
    }
  ]
}
```

Cada item precisa de três campos:

| Campo       | Descrição                                  |
|-------------|--------------------------------------------|
| `titulo`    | Nome curto da atividade.                    |
| `descricao` | Instrução do que fazer durante a pausa.     |
| `icon`      | Um emoji para deixar o card amigável.       |

Você também pode criar **novos tipos de pausa** adicionando uma nova chave no JSON — o sorteio passa a considerá-la automaticamente.

## 🚀 Como rodar localmente

Pré-requisito: **Python 3.10 ou superior**.

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/gerador-pausas-saudaveis.git
cd gerador-pausas-saudaveis

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Rode a aplicação
python main.py
```

> A dependência `customtkinter` é **obrigatória** (interface gráfica). Já a `plyer` é **opcional** — sem ela, o app continua funcionando com o aviso sonoro e o indicador visual; apenas a notificação do sistema operacional fica desativada.

## 🛠️ Tecnologias usadas

- **Python 3.10+**
- **CustomTkinter** (interface gráfica moderna, baseada em Tkinter)
- **json** (carregamento das sugestões, biblioteca padrão)
- **winsound** / bell do terminal (aviso sonoro, biblioteca padrão)
- **plyer** _(opcional)_ — notificações nativas do sistema

## 📁 Estrutura do projeto

```
gerador-pausas-saudaveis/
├── src/
│   ├── data/sugestoes.json   # Atividades por tipo de pausa
│   ├── timer.py              # Lógica da contagem regressiva
│   ├── sugestoes.py          # Carrega e sorteia as sugestões
│   ├── notificacoes.py       # Som + notificação do sistema
│   └── app.py                # Interface e orquestração (CustomTkinter)
├── main.py                   # Ponto de entrada
├── requirements.txt
├── LICENSE
└── README.md
```

## 📄 Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
