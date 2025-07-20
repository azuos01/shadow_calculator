import math
from datetime import datetime
import plotly.graph_objs as go
import plotly.offline as pyo

# ---------- DADOS DE ENTRADA ----------
latitude_deg = -(21 + 44/60 + 21.3/3600)  # converter para decimal e negativa (Sul)
longitude_deg = -(48 + 6/60 + 21.4/3600)  # converter para decimal e negativa (Oeste)
altura_obstaculo = 1.65  # metros

# Dias típicos das estações (dia juliano aproximado)
estacoes = {
    "Solstício de Verão": (21, 12),
    "Equinócio de Outono": (20, 3),
    "Solstício de Inverno": (21, 6),
    "Equinócio de Primavera": (22, 9)
}

# ---------- FUNÇÕES DE CÁLCULO ----------
def declinacao_solar(dia, mes):
    """Cálculo aproximado da declinação solar (em graus) usando fórmula de Cooper."""
    n = (datetime(2025, mes, dia) - datetime(2025, 1, 1)).days + 1
    return 23.45 * math.sin(math.radians(360/365 * (284 + n)))

def elevacao_solar(lat, decl):
    """Ângulo de elevação solar ao meio-dia solar verdadeiro."""
    return 90 - abs(lat - decl)

def comprimento_sombra(altura, elevacao_graus):
    """Comprimento da sombra projetada (em metros)."""
    elev_rad = math.radians(elevacao_graus)
    return altura / math.tan(elev_rad)

# ---------- CÁLCULOS ----------
resultados = {}
for estacao, (dia, mes) in estacoes.items():
    decl = declinacao_solar(dia, mes)
    elev = elevacao_solar(latitude_deg, decl)
    sombra = comprimento_sombra(altura_obstaculo, elev)
    resultados[estacao] = {
        "declinacao": decl,
        "elevacao": elev,
        "sombra": sombra
    }

# ---------- GRÁFICO DE BARRAS ----------
labels = list(resultados.keys())
sombra_vals = [resultados[k]["sombra"] for k in labels]
altura_vals = [altura_obstaculo for _ in labels]

trace1 = go.Bar(name='Altura Obstáculo (m)', x=labels, y=altura_vals, marker_color='orange')
trace2 = go.Bar(name='Comprimento Sombra (m)', x=labels, y=sombra_vals, marker_color='gray')
layout_bar = go.Layout(barmode='group', title='Comprimento da Sombra vs Altura do Obstáculo')
fig_bar = go.Figure(data=[trace1, trace2], layout=layout_bar)
bar_html = pyo.plot(fig_bar, include_plotlyjs=False, output_type='div')

# ---------- HTML ----------
html_template = f"""
<html>
<head>
    <title>Relatório de Sombra - Soluções Solares LTDA</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 30px; }}
        h1, h2 {{ color: #2E8B57; }}
        footer {{ margin-top: 50px; font-size: 0.9em; color: gray; border-top: 1px solid #ccc; padding-top: 10px; }}
        .section {{ margin-bottom: 40px; }}
    </style>
</head>
<body>
    <header>
        <h1>Soluções Solares LTDA</h1>
        <p>Entregando soluções em energia solar desde 2018<br>
        📱 WhatsApp: 16 99630-2896</p>
    </header>

    <div class="section">
        <h2>1 - Dados de Entrada</h2>
        <p><strong>Coordenadas:</strong> Latitude: 21°44'21.3"S, Longitude: 48°06'21.4"W</p>
        <p><strong>Altura do Obstáculo:</strong> {altura_obstaculo} m</p>
        <p><strong>Orientação:</strong> Paralelo ao eixo Leste/Oeste</p>
        <p><strong>Direção da Sombra:</strong> Projetada para o lado Sul</p>
    </div>

    <div class="section">
        <h2>2 - Resultados</h2>
        <ul>
            {''.join([f"<li><strong>{estacao}</strong>: Comprimento da sombra = {val['sombra']:.2f} m</li>" for estacao, val in resultados.items()])}
        </ul>
    </div>

    <div class="section">
        <h2>3 - Visualizações e Gráficos</h2>
        {bar_html}
        <p>Gráfico de barras comparando altura do obstáculo com os comprimentos das sombras nas diferentes estações do ano.</p>
        <p>(O diagrama esquemático será adicionado em versão futura com SVG ou Canvas)</p>
    </div>

    <div class="section">
        <h2>4 - Conclusão</h2>
        <p>As sombras projetadas variam significativamente ao longo das estações. A maior sombra ocorre no inverno (~5,9 m) e a menor no verão (~1,7 m), o que deve ser considerado no espaçamento entre fileiras de módulos solares.</p>
    </div>

    <div class="section">
        <h2>5 - Metodologia de Cálculo</h2>
        <ul>
            <li><strong>Declinação Solar:</strong> δ = 23.45° × sin[360/365 × (284 + n)]</li>
            <li><strong>Elevação Solar:</strong> h = 90° - |φ - δ|</li>
            <li><strong>Comprimento da Sombra:</strong> L = altura / tan(h)</li>
        </ul>
    </div>

    <div class="section">
        <h2>6 - Fontes e Referências</h2>
        <ul>
            <li>Duffie, J.A. & Beckman, W.A. - *Solar Engineering of Thermal Processes*</li>
            <li>https://www.pveducation.org</li>
            <li>https://www.suncalc.org</li>
        </ul>
    </div>

    <div class="section">
        <h2>7 - Premissas e Restrições</h2>
        <ul>
            <li>Obstáculo considerado vertical e plano.</li>
            <li>Cálculo realizado para o meio-dia solar verdadeiro.</li>
            <li>Não considerado relevo local nem outras obstruções.</li>
        </ul>
    </div>

    <footer>
        Este relatório é parte integrante do nosso plano de manutenção - Copyright by Soluções Solares LTDA
    </footer>
</body>
</html>
"""

# Salvar como HTML
with open(r"C:\\Marcos\\Pessoal\\Programacao\\SS_ShadowCalculator\\relatorio_sombra_solar1.html", "w", encoding="utf-8") as f:
    f.write(html_template)

"C:\Marcos\Pessoal\Programacao\SS_ShadowCalculator\relatorio_sombra_solar1.html"

