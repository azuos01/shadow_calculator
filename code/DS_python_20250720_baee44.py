import math
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import base64
from io import BytesIO

# Dados de entrada
dados_entrada = {
    "latitude": {"graus": 21, "minutos": 44, "segundos": 21.3, "direcao": "S"},
    "longitude": {"graus": 48, "minutos": 6, "segundos": 21.4, "direcao": "W"},
    "altura_obstaculo": 1.65,  # metros
    "orientacao_obstaculo": "Paralelo ao eixo Leste/Oeste",
    "direcao_sombra": "Projetada para o lado Sul"
}

# Configurações da empresa
cabecalho = {
    "nome": "Soluções Solares LTDA",
    "slogan": "Entregando soluções em energia solar desde 2018",
    "whatsapp": "16 99630-2896"
}

rodape = "Este relatório é parte integrante do nosso plano de manutenção - Copyright by Soluções Solares LTDA"

# Funções para cálculos solares
def graus_para_decimal(graus, minutos, segundos, direcao):
    decimal = graus + minutos/60 + segundos/3600
    if direcao in ['S', 'W']:
        decimal *= -1
    return decimal

def calcular_declinacao_solar(dia_ano):
    return 23.45 * math.sin(math.radians(360 * (284 + dia_ano) / 365))

def calcular_elevacao_solar(latitude, declinacao, angulo_horario):
    lat_rad = math.radians(latitude)
    dec_rad = math.radians(declinacao)
    return math.degrees(math.asin(
        math.sin(lat_rad) * math.sin(dec_rad) + 
        math.cos(lat_rad) * math.cos(dec_rad) * math.cos(math.radians(angulo_horario))
    ))

def calcular_comprimento_sombra(altura, elevacao_solar):
    if elevacao_solar <= 0:
        return float('inf')  # O sol está abaixo do horizonte
    return altura / math.tan(math.radians(elevacao_solar))

# Datas representativas das estações (2023 como exemplo)
datas_estacoes = {
    "Solstício de Verão": {"data": "2023-12-21", "dia_ano": 355},
    "Solstício de Inverno": {"data": "2023-06-21", "dia_ano": 172},
    "Equinócio de Primavera": {"data": "2023-09-23", "dia_ano": 266},
    "Equinócio de Outono": {"data": "2023-03-20", "dia_ano": 79}
}

# Converter coordenadas para decimal
latitude_decimal = graus_para_decimal(
    dados_entrada["latitude"]["graus"],
    dados_entrada["latitude"]["minutos"],
    dados_entrada["latitude"]["segundos"],
    dados_entrada["latitude"]["direcao"]
)

# Cálculos para cada estação
resultados = {}
for estacao, info in datas_estacoes.items():
    declinacao = calcular_declinacao_solar(info["dia_ano"])
    # Usamos meio-dia solar (ângulo horário = 0) para máxima sombra no eixo norte-sul
    elevacao = calcular_elevacao_solar(latitude_decimal, declinacao, 0)
    comprimento_sombra = calcular_comprimento_sombra(dados_entrada["altura_obstaculo"], elevacao)
    
    resultados[estacao] = {
        "declinacao": declinacao,
        "elevacao_solar": elevacao,
        "comprimento_sombra": comprimento_sombra,
        "data": info["data"]
    }

# Gerar gráficos
def gerar_grafico_barras(resultados, altura_obstaculo):
    estacoes = list(resultados.keys())
    sombras = [r["comprimento_sombra"] for r in resultados.values()]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.4
    
    # Barras para o obstáculo
    bars1 = ax.bar([x - bar_width/2 for x in range(len(estacoes))], 
                  [altura_obstaculo]*len(estacoes), 
                  bar_width, label='Altura do Obstáculo (1.65m)', color='darkblue')
    
    # Barras para as sombras
    bars2 = ax.bar([x + bar_width/2 for x in range(len(estacoes))], 
                  sombras, 
                  bar_width, label='Comprimento da Sombra', color='orange')
    
    ax.set_xlabel('Estações do Ano')
    ax.set_ylabel('Metros')
    ax.set_title('Comparação entre Altura do Obstáculo e Comprimento da Sombra')
    ax.set_xticks(range(len(estacoes)))
    ax.set_xticklabels(estacoes, rotation=45, ha='right')
    ax.legend()
    
    # Adicionar valores nas barras
    for bar in bars1 + bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}m',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Converter para base64
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def gerar_diagrama_sombra(resultados, altura_obstaculo):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['red', 'blue', 'green', 'purple']
    for i, (estacao, info) in enumerate(resultados.items()):
        comprimento = info["comprimento_sombra"]
        if comprimento == float('inf'):
            continue  # Não plotar sombras infinitas
        
        # Obstáculo
        ax.add_patch(Rectangle((0, 0), 0.5, altura_obstaculo, fill=True, color='gray'))
        
        # Sombra
        ax.plot([0.25, 0.25 + comprimento/5], [0, 0], 
                linestyle='-', linewidth=3, color=colors[i], label=estacao)
        
        # Ângulo
        ax.plot([0.25, 0.25 + comprimento/5], [altura_obstaculo, 0], 
                linestyle='--', linewidth=1, color=colors[i])
    
    ax.set_xlim(0, max([r["comprimento_sombra"]/5 for r in resultados.values() if r["comprimento_sombra"] != float('inf')]) + 1)
    ax.set_ylim(0, altura_obstaculo + 1)
    ax.set_xlabel('Distância (m) - Escala Reduzida')
    ax.set_ylabel('Altura (m)')
    ax.set_title('Diagrama Esquemático das Sombras Sazonais')
    ax.legend()
    ax.grid(True)
    
    # Converter para base64
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

# Gerar os gráficos
grafico_barras = gerar_grafico_barras(resultados, dados_entrada["altura_obstaculo"])
diagrama_sombra = gerar_diagrama_sombra(resultados, dados_entrada["altura_obstaculo"])

# HTML template
html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Projeção de Sombras</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-bottom: 3px solid #007bff;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #007bff;
            margin-bottom: 5px;
        }}
        .header p {{
            margin-top: 5px;
            font-size: 1.1em;
        }}
        .section {{
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        .section h2 {{
            color: #007bff;
            border-left: 5px solid #007bff;
            padding-left: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        table, th, td {{
            border: 1px solid #ddd;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .graph-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 20px 0;
        }}
        .graph {{
            max-width: 800px;
            margin: 10px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            background-color: #f8f9fa;
            font-size: 0.9em;
            color: #666;
        }}
        .coordinate {{
            font-family: monospace;
            background-color: #f5f5f5;
            padding: 2px 5px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{cabecalho['nome']}</h1>
        <p>{cabecalho['slogan']}</p>
        <p>📱 WhatsApp: {cabecalho['whatsapp']}</p>
    </div>

    <div class="section">
        <h2>1 - Dados de Entrada</h2>
        <p>Os seguintes dados foram utilizados para os cálculos:</p>
        <table>
            <tr>
                <th>Parâmetro</th>
                <th>Valor</th>
            </tr>
            <tr>
                <td>Coordenadas Geográficas</td>
                <td>
                    Latitude: <span class="coordinate">{dados_entrada["latitude"]["graus"]}°{dados_entrada["latitude"]["minutos"]}'{dados_entrada["latitude"]["segundos"]}"{dados_entrada["latitude"]["direcao"]}</span><br>
                    Longitude: <span class="coordinate">{dados_entrada["longitude"]["graus"]}°{dados_entrada["longitude"]["minutos"]}'{dados_entrada["longitude"]["segundos"]}"{dados_entrada["longitude"]["direcao"]}</span><br>
                    (Decimal: {latitude_decimal:.6f}°)
                </td>
            </tr>
            <tr>
                <td>Altura do Obstáculo</td>
                <td>{dados_entrada["altura_obstaculo"]} metros</td>
            </tr>
            <tr>
                <td>Orientação do Obstáculo</td>
                <td>{dados_entrada["orientacao_obstaculo"]}</td>
            </tr>
            <tr>
                <td>Direção da Sombra</td>
                <td>{dados_entrada["direcao_sombra"]}</td>
            </tr>
        </table>
    </div>

    <div class="section">
        <h2>2 - Resultados</h2>
        <p>Comprimento máximo da sombra projetada pelo obstáculo nas diferentes estações do ano:</p>
        <table>
            <tr>
                <th>Estação do Ano</th>
                <th>Data Representativa</th>
                <th>Declinação Solar</th>
                <th>Elevação Solar ao Meio-Dia</th>
                <th>Comprimento da Sombra</th>
            </tr>
            {"".join([f"""
            <tr>
                <td>{estacao}</td>
                <td>{info['data']}</td>
                <td>{info['declinacao']:.2f}°</td>
                <td>{info['elevacao_solar']:.2f}°</td>
                <td>{'Infinita (Sol abaixo do horizonte)' if info['comprimento_sombra'] == float('inf') else f"{info['comprimento_sombra']:.2f} metros"}</td>
            </tr>
            """ for estacao, info in resultados.items()])}
        </table>
    </div>

    <div class="section">
        <h2>3 - Visualizações e Gráficos</h2>
        
        <h3>Comparação entre Altura do Obstáculo e Comprimento da Sombra</h3>
        <div class="graph-container">
            <img src="data:image/png;base64,{grafico_barras}" alt="Gráfico de Barras" class="graph">
        </div>
        
        <h3>Diagrama Esquemático das Sombras Sazonais</h3>
        <div class="graph-container">
            <img src="data:image/png;base64,{diagrama_sombra}" alt="Diagrama de Sombras" class="graph">
            <p><em>Nota: O diagrama está em escala reduzida para melhor visualização.</em></p>
        </div>
    </div>

    <div class="section">
        <h2>4 - Conclusão</h2>
        <p>Com base nos cálculos realizados, observamos que o comprimento da sombra projetada pelo obstáculo varia significativamente ao longo das estações do ano:</p>
        <ul>
            <li>No <strong>Solstício de Verão</strong>, quando o Sol atinge sua posição mais alta no céu, a sombra projetada é a mais curta do ano.</li>
            <li>No <strong>Solstício de Inverno</strong>, com o Sol em sua posição mais baixa, a sombra atinge seu comprimento máximo.</li>
            <li>Nos <strong>Equinócios</strong> (Primavera e Outono), o comprimento da sombra apresenta valores intermediários.</li>
        </ul>
        <p>Estas variações devem ser consideradas no planejamento de sistemas fotovoltaicos para evitar sombreamento nos painéis solares em qualquer época do ano.</p>
    </div>

    <div class="section">
        <h2>5 - Metodologia de Cálculo</h2>
        <p>Os cálculos foram realizados com base nas seguintes fórmulas astronômicas:</p>
        
        <h3>Cálculo da Declinação Solar (δ)</h3>
        <p>δ = 23.45° × sin[360° × (284 + n) / 365]</p>
        <p>Onde n é o dia do ano (1 a 365).</p>
        
        <h3>Cálculo do Ângulo Horário Solar (ω)</h3>
        <p>Para o cálculo da sombra ao meio-dia solar, utilizamos ω = 0°.</p>
        
        <h3>Cálculo da Elevação Solar (α)</h3>
        <p>α = arcsin[sin(φ) × sin(δ) + cos(φ) × cos(δ) × cos(ω)]</p>
        <p>Onde φ é a latitude do local.</p>
        
        <h3>Cálculo do Comprimento da Sombra (L)</h3>
        <p>L = h / tan(α)</p>
        <p>Onde h é a altura do obstáculo e α é a elevação solar.</p>
    </div>

    <div class="section">
        <h2>6 - Fontes e Referências</h2>
        <ul>
            <li>Iqbal, M. (1983). <em>An Introduction to Solar Radiation</em>. Academic Press.</li>
            <li>Duffie, J. A., & Beckman, W. A. (2013). <em>Solar Engineering of Thermal Processes</em>. Wiley.</li>
            <li>NOAA Solar Calculator. National Oceanic and Atmospheric Administration.</li>
            <li>Reda, I., & Andreas, A. (2008). Solar Position Algorithm for Solar Radiation Applications. <em>NREL Technical Report</em>.</li>
        </ul>
    </div>

    <div class="section">
        <h2>7 - Premissas e Restrições</h2>
        <p>Os resultados apresentados estão sujeitos às seguintes condições:</p>
        <ul>
            <li>Cálculos válidos para o ano de 2023, mas com pequena variação anual.</li>
            <li>Considera-se condições atmosféricas ideais (sem efeitos de nebulosidade ou refração).</li>
            <li>O obstáculo é modelado como uma barreira vertical perfeita.</li>
            <li>O terreno é considerado plano e nivelado.</li>
            <li>Não são considerados obstáculos adicionais no entorno.</li>
            <li>Para aplicações críticas, recomenda-se verificação in loco nos períodos de interesse.</li>
        </ul>
    </div>

    <div class="footer">
        {rodape}
    </div>
</body>
</html>
"""

# Salvar o HTML em um arquivo
with open('relatorio_sombras_solares.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("Relatório HTML gerado com sucesso: relatorio_sombras_solares.html")