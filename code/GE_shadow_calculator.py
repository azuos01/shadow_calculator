import math
from datetime import datetime

def dms_to_decimal(degrees, minutes, seconds, direction):
    """Converte graus, minutos, segundos para formato decimal."""
    decimal_degrees = degrees + minutes / 60 + seconds / 3600
    if direction in ['S', 'W']:
        return -decimal_degrees
    return decimal_degrees

def calculate_solar_declination(day_of_year):
    """Calcula a declinação solar em radianos."""
    # Fórmulas para declinação solar podem variar ligeiramente. Esta é uma aproximação comum.
    return 0.409 * math.sin(((2 * math.pi / 365) * day_of_year) - 1.39)

def calculate_hour_angle(local_time_decimal, longitude, standard_meridian):
    """Calcula o ângulo horário solar em radianos.
    Para o cálculo da sombra máxima ao meio-dia solar, o ângulo horário é 0.
    """
    # Para o propósito deste relatório, focamos na sombra ao meio-dia solar,
    # onde o sol está mais alto e a sombra é a mais curta, geralmente.
    # Se a intenção fosse calcular a sombra para um horário específico ou o pior cenário
    # de sombra longa em outro momento, esta função seria mais complexa.
    return 0 # Ao meio-dia solar, o ângulo horário é 0.

def calculate_solar_elevation(latitude, declination, hour_angle):
    """Calcula o ângulo de elevação solar em radianos."""
    lat_rad = math.radians(latitude)
    
    sin_alpha = (math.sin(lat_rad) * math.sin(declination)) + \
                (math.cos(lat_rad) * math.cos(declination) * math.cos(hour_angle))
    
    # Garantir que o argumento para asin esteja no intervalo [-1, 1] devido a pequenas imprecisões de ponto flutuante
    sin_alpha = max(-1.0, min(1.0, sin_alpha))
    
    elevation_rad = math.asin(sin_alpha)
    
    # Se a elevação for negativa (sol abaixo do horizonte), a sombra é "infinita" ou não visível no plano horizontal
    return elevation_rad if elevation_rad > 0 else 0

def calculate_shadow_length(obstacle_height, solar_elevation):
    """Calcula o comprimento da sombra."""
    if solar_elevation <= 0:
        return float('inf')  # Sombra infinita ou muito longa se o sol estiver abaixo/no horizonte
    return obstacle_height / math.tan(solar_elevation)

# --- Dados de Entrada ---
latitude_dms = (21, 44, 21.3, 'S')
longitude_dms = (48, 6, 21.4, 'W')
obstacle_height = 1.65  # metros
obstacle_orientation = "Paralelo ao eixo Leste/Oeste"
shadow_direction = "Projetada para o lado Sul"

# Personalização
header_title = "Soluções Solares LTDA"
header_subtitle = "Entregando soluções em energia solar desde 2018"
header_whatsapp = "📱 WhatsApp: 16 99630-2896"
footer_text = "Este relatório é parte integrante do nosso plano de manutenção - Copyright by Soluções Solares LTDA"

# Converter coordenadas para decimal
latitude = dms_to_decimal(latitude_dms[0], latitude_dms[1], latitude_dms[2], latitude_dms[3])
longitude = dms_to_decimal(longitude_dms[0], longitude_dms[1], longitude_dms[2], longitude_dms[3])

# Coordenadas do ponto geográfico formatadas para exibição
lat_str = f"{abs(latitude_dms[0])}°{latitude_dms[1]}'{latitude_dms[2]}\"{latitude_dms[3]}"
lon_str = f"{abs(longitude_dms[0])}°{longitude_dms[1]}'{longitude_dms[2]}\"{longitude_dms[3]}"

# --- Cálculos para as Estações do Ano (Dia do Ano aproximado para o Hemisfério Sul) ---
# Hemisfério Sul:
# Solstício de Verão: 21 de Dezembro (aprox. Dia do Ano 355) - Sol mais alto, sombra mais curta
# Solstício de Inverno: 21 de Junho (aprox. Dia do Ano 172) - Sol mais baixo, sombra mais longa
# Equinócio de Primavera: 22 de Setembro (aprox. Dia do Ano 265)
# Equinócio de Outono: 20 de Março (aprox. Dia do Ano 79)

seasons = {
    "Solstício de Verão (21 Dez)": 355,
    "Solstício de Inverno (21 Jun)": 172,
    "Equinócio de Primavera (22 Set)": 265,
    "Equinócio de Outono (20 Mar)": 79
}

shadow_results = {}
calculation_details = {}

for season, day_of_year in seasons.items():
    declination = calculate_solar_declination(day_of_year)
    hour_angle = calculate_hour_angle(12.0, longitude, -45) # Assumindo 12h para o solstício e meridiano padrão de -45 (GMT-3)
    solar_elevation = calculate_solar_elevation(latitude, declination, hour_angle)
    shadow_length = calculate_shadow_length(obstacle_height, solar_elevation)
    
    shadow_results[season] = shadow_length
    calculation_details[season] = {
        "Declinação Solar (graus)": math.degrees(declination),
        "Ângulo Horário Solar (graus)": math.degrees(hour_angle),
        "Elevação Solar (graus)": math.degrees(solar_elevation),
        "Comprimento da Sombra (m)": shadow_length
    }

# Encontrar o comprimento máximo da sombra para escalonar os gráficos
max_shadow_for_scaling = 0
for length in shadow_results.values():
    if length != float('inf'): # Ignore infinity for scaling
        max_shadow_for_scaling = max(max_shadow_for_scaling, length)
if max_shadow_for_scaling == 0: # Avoid division by zero if all shadows are infinity
    max_shadow_for_scaling = obstacle_height * 2 # Fallback scaling

# Definir as fórmulas LaTeX como strings raw separadas
latex_declination_formula = r"$$ \delta = 0.409 \cdot \sin\left(\frac{2\pi}{365} \cdot \text{Dia do Ano} - 1.39\right) $$"
latex_hour_angle_formula = r"$$ \omega = 15 \cdot (\text{LST} - 12) $$"
latex_elevation_formula = r"$$ \sin(\alpha) = \sin(\phi) \cdot \sin(\delta) + \cos(\phi) \cdot \cos(\delta) \cdot \cos(\omega) $$"
latex_shadow_length_formula = r"$$ L = \frac{\text{Altura do Obstáculo}}{\tan(\alpha)} $$"

# --- Geração do HTML ---
html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Sombra Solar</title>
    <script type="text/javascript" async
      src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
    </script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f4f7f6;
        }}
        .container {{
            max-width: 960px;
            margin: 20px auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        header {{
            text-align: center;
            padding: 20px 0;
            background: linear-gradient(to right, #007bff, #0056b3);
            color: #fff;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        header h1 {{
            margin: 0;
            font-size: 2.5em;
            letter-spacing: 1px;
        }}
        header p {{
            margin: 5px 0;
            font-size: 1.1em;
            opacity: 0.9;
        }}
        footer {{
            text-align: center;
            padding: 15px 0;
            background: #0056b3;
            color: #fff;
            border-radius: 8px;
            margin-top: 30px;
            font-size: 0.85em;
        }}
        h1, h2, h3 {{
            color: #0056b3;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 8px;
            margin-top: 40px;
            margin-bottom: 20px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        ul {{
            list-style-type: disc;
            padding-left: 25px;
        }}
        li {{
            margin-bottom: 10px;
        }}
        .code-block {{
            background-color: #f0f4f7;
            border: 1px solid #dcdcdc;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            white-space: pre-wrap; /* Permite quebras de linha */
            word-wrap: break-word; /* Força quebra de palavras longas */
            font-family: 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
            font-size: 0.95em;
            color: #333;
            margin-top: 15px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 1px 5px rgba(0,0,0,0.05);
        }}
        th, td {{
            border: 1px solid #e0e0e0;
            padding: 12px 15px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
            color: #555;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .note {{
            font-style: italic;
            color: #6a6a6a;
            margin-top: 15px;
            padding: 10px;
            border-left: 4px solid #007bff;
            background-color: #e6f3ff;
            border-radius: 4px;
        }}
        .visualization-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 40px;
            margin-top: 30px;
        }}
        .chart-title {{
            text-align: center;
            color: #0056b3;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        .bar-chart-actual, .schematic-diagram-actual {{
            width: 90%; /* Ajuste a largura conforme necessário */
            height: 350px;
            background-color: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            position: relative;
            padding: 20px;
            box-sizing: border-box;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            overflow: hidden; /* Garante que elementos fora não causem scroll */
        }}
        .bar-chart-actual {{
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            padding-bottom: 30px; /* Espaço para labels */
        }}
        .bar-group {{
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100%;
            justify-content: flex-end;
            position: relative;
            width: 100px; /* Largura do grupo de barras */
        }}
        .bar {{
            width: 40px;
            background-color: #007bff;
            margin: 0 5px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            color: white;
            font-size: 0.8em;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
            position: relative; /* Para o valor no topo */
            transition: height 0.5s ease-out;
        }}
        .bar-value {{
            position: absolute;
            top: -20px;
            font-size: 0.75em;
            color: #333;
            white-space: nowrap;
        }}
        .bar-label-group {{
            position: absolute;
            bottom: -25px;
            font-size: 0.8em;
            color: #555;
            text-align: center;
            width: 100%;
        }}
        .obstacle-bar {{
            background-color: #dc3545;
        }}
        .shadow-bar {{
            background-color: #28a745;
        }}
        .axis-y-chart {{
            position: absolute;
            left: 20px;
            bottom: 30px;
            top: 20px;
            width: 2px;
            background-color: #ccc;
        }}
        .y-tick-chart {{
            position: absolute;
            left: 17px;
            width: 6px;
            height: 1px;
            background-color: #888;
        }}
        .y-label-chart {{
            position: absolute;
            left: -15px; /* Ajuste para centralizar */
            font-size: 0.7em;
            color: #666;
            text-align: right;
            width: 40px;
            transform: translateY(50%);
        }}

        /* Schematic Diagram */
        .diagram-obstacle {{
            position: absolute;
            bottom: 20px; /* Altura do chão */
            left: 50%;
            transform: translateX(-50%);
            width: 20px;
            background-color: #dc3545;
            text-align: center;
            color: white;
            font-size: 0.7em;
            line-height: 1.2;
            padding-top: 5px;
            box-shadow: 0 0 5px rgba(0,0,0,0.2);
            z-index: 2; /* Para ficar acima da sombra */
        }}
        .diagram-ground {{
            position: absolute;
            bottom: 19px; /* Um pixel abaixo da base do obstáculo */
            left: 0;
            width: 100%;
            height: 2px;
            background-color: #555;
            z-index: 1;
        }}
        .diagram-shadow {{
            position: absolute;
            bottom: 20px; /* Altura do chão */
            background-color: rgba(40, 167, 69, 0.5); /* Verde com transparência */
            height: 10px; /* Espessura da sombra */
            border-radius: 5px;
            z-index: 1;
            transform-origin: center center; /* Para escalonamento */
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 0.7em;
            white-space: nowrap;
        }}
        .sun-ray {{
            position: absolute;
            background-color: rgba(255, 165, 0, 0.7); /* Laranja com transparência */
            width: 2px;
            transform-origin: bottom center; /* Origem da rotação na base do obstáculo */
            z-index: 0;
        }}
        .sun-label {{
            position: absolute;
            font-size: 0.8em;
            color: #333;
            background-color: rgba(255,255,255,0.8);
            padding: 2px 5px;
            border-radius: 3px;
            white-space: nowrap;
            z-index: 3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{header_title}</h1>
            <p>{header_subtitle}</p>
            <p>{header_whatsapp}</p>
        </header>

        <section class="section">
            <h2>1 - Dados de Entrada</h2>
            <ul>
                <li><strong>Coordenadas do ponto geográfico:</strong> Latitude: {lat_str}, Longitude: {lon_str}</li>
                <li><strong>Altura do obstáculo:</strong> {obstacle_height} m</li>
                <li><strong>Orientação do obstáculo:</strong> {obstacle_orientation}</li>
                <li><strong>Direção da sombra:</strong> {shadow_direction}</li>
            </ul>
        </section>

        ---

        <section class="section">
            <h2>2 - Resultados</h2>
            <p>Qual a distância máxima da sombra que um obstáculo de **{obstacle_height}m** projeta durante as 4 estações do ano ao meio-dia solar?</p>
            <table>
                <thead>
                    <tr>
                        <th>Estação</th>
                        <th>Comprimento da Sombra (m)</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'<tr><td>{season}</td><td>{length:.2f} m</td></tr>' if length != float('inf') else f'<tr><td>{season}</td><td>Sombra infinita (Sol abaixo do horizonte)</td></tr>' for season, length in shadow_results.items()])}
                </tbody>
            </table>
            <p class="note">
                <em>**Nota:** Os resultados representam o comprimento da sombra ao **meio-dia solar local** para cada estação. Este é o momento em que o sol atinge sua elevação máxima diária, resultando na sombra mais curta. Como o local está no Hemisfério Sul, ao meio-dia solar, o sol estará sempre posicionado ao Norte do observador, projetando a sombra para o Sul. Em casos de elevação solar zero ou negativa (sol abaixo do horizonte), a sombra é considerada infinita.</em>
            </p>
        </section>

        ---

        <section class="section">
            <h2>3 - Visualizações e Gráficos</h2>
            <p>Uma análise completa das sombras sazonais, incluindo comparações e variações.</p>

            <h3 class="chart-title">Gráfico de Barras do Comprimento das Sombras Sazonais</h3>
            <p>Este gráfico compara a altura do obstáculo com o comprimento da sombra projetada para cada estação do ano, fornecendo uma visualização clara da variação sazonal.</p>
            <div class="bar-chart-actual">
                <div class="axis-y-chart"></div>
                <span class="y-label-chart" style="top: 0px; transform: translateY(-50%);">Comprimento (m)</span>
                
                <div class="y-tick-chart" style="bottom: 0%;"></div><span class="y-label-chart" style="bottom: -5px;">0.0</span>
                {''.join([f'''
                    <div class="y-tick-chart" style="bottom: {(val / max_shadow_for_scaling) * 100}%;"></div>
                    <span class="y-label-chart" style="bottom: {(val / max_shadow_for_scaling) * 100 - 5}px;">{val:.1f}</span>
                ''' for val in [max_shadow_for_scaling * 0.2, max_shadow_for_scaling * 0.4, max_shadow_for_scaling * 0.6, max_shadow_for_scaling * 0.8, max_shadow_for_scaling]])}

                {''.join([f'''
                    <div class="bar-group">
                        <div class="bar obstacle-bar" style="height: {(obstacle_height / max_shadow_for_scaling * 80 if max_shadow_for_scaling > 0 else 0)}%;">
                            <span class="bar-value">{obstacle_height:.2f}m</span>
                        </div>
                        <div class="bar shadow-bar" style="height: {(shadow_results[season] / max_shadow_for_scaling * 80 if max_shadow_for_scaling > 0 and shadow_results[season] != float('inf') else 0)}%;">
                            <span class="bar-value">{'Inf.' if shadow_results[season] == float('inf') else f'{shadow_results[season]:.2f}m'}</span>
                        </div>
                        <span class="bar-label-group">{season.split(" ")[0]}</span>
                    </div>
                ''' for season in seasons.keys()])}
            </div>
            <p class="note">
                <em>**As alturas das barras são proporcionais ao comprimento máximo de sombra calculado** (ignorando "infinito") para garantir uma visualização comparável. Barras de "Sombra infinita" indicam que o sol estava abaixo do horizonte ao meio-dia solar.</em>
            </p>

            <h3 class="chart-title">Diagrama Esquemático de Sombras Sazonais</h3>
            <p>Este diagrama ilustra a projeção da sombra do obstáculo em relação à altura do sol em diferentes estações do ano, mostrando como o ângulo solar afeta o comprimento da sombra.</p>
            <div class="schematic-diagram-actual">
                <div class="diagram-ground"></div>
                <div class="diagram-obstacle" style="height: {obstacle_height * 50}px;">Obstáculo<br>({obstacle_height}m)</div>
                {''.join([f'''
                    {'<div class="diagram-shadow" style="width: ' + str(shadow_results[season] * 50) + 'px; left: calc(50% - ' + str(shadow_results[season] * 50 / 2) + 'px);">' + season.split(" ")[0] + '</div>' if shadow_results[season] != float('inf') else ''}
                    {'<div class="sun-ray" style="height: ' + str(math.sqrt((obstacle_height * 50)**2 + (shadow_results[season] * 50)**2)) + 'px; transform: rotate(' + str(-(90 - math.degrees(math.atan2(obstacle_height, shadow_results[season])))) + 'deg); left: calc(50% - ' + str(10 if obstacle_height > 0 else 0) + 'px); bottom: ' + str(obstacle_height * 50 + 20) + 'px;"></div>' if shadow_results[season] != float('inf') and obstacle_height > 0 else ''}
                    {'<span class="sun-label" style="top: ' + str(20 + (obstacle_height * 50 * 0.1) - (shadow_results[season] * 50 * 0.05)) + 'px; left: calc(50% - ' + str(shadow_results[season] * 50 / 2) + 'px + ' + str(shadow_results[season] * 50 * 0.7) + 'px); transform: rotate(' + str(-(90 - math.degrees(math.atan2(obstacle_height, shadow_results[season])))) + 'deg);">' + season.split(" ")[0] + ' Sol</span>' if shadow_results[season] != float('inf') else ''}
                ''' for season, length in shadow_results.items()])}
                <p class="note">
                    <em>Este diagrama é uma representação esquemática. **As escalas são aproximadas** para fins visuais (1m ≈ 50px). A sombra é projetada para o Sul no Hemisfério Sul ao meio-dia solar. Raios solares e sombras para "Sombra Infinita" não são exibidos neste diagrama.</em>
                </p>
            </div>
        </section>

        ---

        <section class="section">
            <h2>4 - Conclusão</h2>
            <p>Este relatório detalhou a projeção da sombra de um obstáculo de **{obstacle_height} metros** de altura em **{lat_str}, {lon_str}** ao longo das quatro estações do ano. Os resultados indicam que o comprimento da sombra varia significativamente, sendo consistentemente **mais longa no Solstício de Inverno** (quando o sol está mais baixo no horizonte) e **mais curta no Solstício de Verão** (quando o sol está mais alto).</p>
            <p>Essa variação sazonal é de **crucial importância** para o planejamento e otimização de instalações solares, como sistemas fotovoltaicos. Garantir que os painéis não sejam sombreados, especialmente durante as horas de pico de irradiação solar, é fundamental para maximizar a captação de energia e evitar perdas de eficiência. A projeção da sombra sempre para o Sul ao meio-dia solar, neste local do Hemisfério Sul, reafirma a necessidade de se considerar a inclinação e orientação ideais para os painéis.</p>
            <p>Em suma, a análise demonstrou a importância de se realizar **estudos de sombreamento detalhados e sazonais** para prever o comportamento da sombra e otimizar o desempenho de qualquer sistema dependente da energia solar, contribuindo para soluções energéticas mais eficientes e sustentáveis.</p>
        </section>

        ---

        <section class="section">
            <h2>5 - Metodologia de Cálculo</h2>
            <p>Os cálculos para determinar o comprimento da sombra baseiam-se em princípios de geometria solar e astronomia. As principais etapas e fórmulas utilizadas são:</p>
            
            <h3>Cálculo da Declinação Solar ($$\delta$$)</h3>
            <p>A declinação solar é o ângulo entre os raios solares e o plano do equador terrestre. Ela varia ao longo do ano devido à inclinação do eixo da Terra em relação à sua órbita. É calculada pela fórmula:</p>
            <div class="code-block">
                {latex_declination_formula}
            </div>
            <p>Onde Dia do Ano é o número do dia no ano (1 para 1º de janeiro, etc.).</p>

            <h3>Cálculo do Ângulo Horário Solar ($$\\omega$$)</h3>
            <p>O ângulo horário solar descreve a posição angular do sol a leste ou oeste do meridiano local. Ao meio-dia solar local, o ângulo horário é 0. Para o foco deste relatório na sombra mais curta (meio-dia solar), o ângulo horário é considerado zero.</p>
            <div class="code-block">
                {latex_hour_angle_formula}
            </div>
            <p>Onde LST é o Tempo Solar Local. Para o meio-dia solar, $$ \\omega $$ é 0.</p>

            <h3>Cálculo da Elevação Solar ($$\\alpha$$)</h3>
            <p>A elevação solar (ou ângulo de altitude solar) é o ângulo entre os raios solares e o plano horizontal. É um fator crítico para determinar o comprimento da sombra. A fórmula utilizada é:</p>
            <div class="code-block">
                {latex_elevation_formula}
            </div>
            <p>Onde:</p>
            <ul>
                <li>$$\\alpha$$ é a elevação solar (ângulo de altitude)</li>
                <li>$$\\phi$$ é a latitude do local</li>
                <li>$$\\delta$$ é a declinação solar</li>
                <li>$$\\omega$$ é o ângulo horário solar</li>
            </ul>

            <h3>Cálculo do Comprimento da Sombra ($$L$$)</h3>
            <p>O comprimento da sombra projetada por um obstáculo é calculado usando trigonometria simples, com base na altura do obstáculo e no ângulo de elevação solar:</p>
            <div class="code-block">
                {latex_shadow_length_formula}
            </div>
            <p>Se o ângulo de elevação for zero ou negativo (sol abaixo do horizonte), a sombra é considerada infinita ou extremamente longa.</p>
            <p>Os valores de declinação, ângulo horário e elevação foram calculados para o meio-dia solar de cada data representativa das estações do ano, que é o momento de maior elevação solar diária e, consequentemente, a sombra mais curta.</p>
        </section>

        ---

        <section class="section">
            <h2>6 - Fontes e Referências</h2>
            <ul>
                <li>**Duffie, J. A., & Beckman, W. A.** (2013). <em>Solar Engineering of Thermal Processes</em>. John Wiley & Sons. (Referência fundamental em engenharia solar)</li>
                <li>**The National Renewable Energy Laboratory (NREL)** - <a href="https://www.nrel.gov" target="_blank">www.nrel.gov</a> (Fonte de pesquisa e dados sobre energia renovável)</li>
                <li>**Global Solar Atlas** - <a href="https://globalsolaratlas.info/" target="_blank">globalsolaratlas.info</a> (Ferramenta interativa com dados de irradiação solar global)</li>
                <li>**PV Education** - <a href="https://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-angles" target="_blank">Solar Angles</a> (Artigos educativos sobre ângulos solares e fotovoltaica)</li>
            </ul>
        </section>

        ---

        <section class="section">
            <h2>7 - Premissas e Restrições</h2>
            <ul>
                <li>**Localização Geográfica:** Os cálculos são específicos para as coordenadas fornecidas ({lat_str}, {lon_str}). Pequenas variações na localização podem impactar os resultados.</li>
                <li>**Datas das Estações:** As datas para os solstícios e equinócios são aproximadas. Variações anuais podem ocorrer, embora geralmente pequenas.</li>
                <li>**Hora de Cálculo:** Os comprimentos de sombra foram calculados especificamente para o **meio-dia solar local**. Este é o ponto do dia com a maior elevação solar e, portanto, a menor projeção de sombra. Para uma análise completa do sombreamento ao longo de um dia inteiro, seria necessário um modelo horário mais detalhado.</li>
                <li>**Terreno Plano:** Assume-se que o terreno ao redor do obstáculo é perfeitamente plano. Irregularidades topográficas (colinas, vales) podem alterar significativamente a projeção real da sombra.</li>
                <li>**Atmosfera Padrão:** Os cálculos da elevação solar assumem condições atmosféricas padrão. Efeitos de refração atmosférica ou dispersão de luz não são considerados, embora tenham impacto marginal.</li>
                <li>**Obstáculo Idealizado:** O obstáculo é tratado como um objeto vertical e ideal. Formatos complexos ou inclinações do obstáculo exigiriam modelagem mais avançada.</li>
                <li>**Resultados de Previsão:** Os dados apresentados são previsões baseadas em modelos matemáticos e não em medições de campo reais. Fatores ambientais não modelados podem levar a pequenas discrepâncias.</li>
            </ul>
        </section>

        <footer>
            <p>{footer_text}</p>
        </footer>
    </div>
</body>
</html>
"""


# Salvar o conteúdo HTML em um arquivo
file_path = "relatorio_sombra_solar_GE.html"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Relatório HTML gerado com sucesso em: {file_path}")
print("\nVocê pode abrir este arquivo no seu navegador para visualizar a apresentação.")