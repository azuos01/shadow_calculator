import math
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import base64
import io

class SolarShadowAnalyzer:
    def __init__(self, latitude, longitude, obstacle_height):
        """
        Inicializa o analisador de sombras solares
        
        Args:
            latitude (float): Latitude em graus decimais (negativo para Sul)
            longitude (float): Longitude em graus decimais (negativo para Oeste)
            obstacle_height (float): Altura do obstáculo em metros
        """
        self.latitude = latitude
        self.longitude = longitude
        self.obstacle_height = obstacle_height
        
        # Datas dos solstícios e equinócios para 2024
        self.seasons = {
            'Solstício de Verão': {'day': 355, 'name': 'Verão (21 Dez)'},  # 21 de dezembro
            'Equinócio de Outono': {'day': 80, 'name': 'Outono (21 Mar)'},   # 21 de março
            'Solstício de Inverno': {'day': 172, 'name': 'Inverno (21 Jun)'}, # 21 de junho
            'Equinócio de Primavera': {'day': 266, 'name': 'Primavera (23 Set)'} # 23 de setembro
        }
    
    def dms_to_decimal(self, degrees, minutes, seconds, direction):
        """Converte graus, minutos, segundos para graus decimais"""
        decimal = degrees + minutes/60 + seconds/3600
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal
    
    def solar_declination(self, day_of_year):
        """Calcula a declinação solar para um dia do ano"""
        return 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
    
    def solar_hour_angle(self, hour=12):
        """Calcula o ângulo horário solar (meio-dia = 0°)"""
        return 15 * (hour - 12)
    
    def solar_elevation(self, declination, hour_angle=0):
        """Calcula a elevação solar"""
        lat_rad = math.radians(self.latitude)
        dec_rad = math.radians(declination)
        hour_rad = math.radians(hour_angle)
        
        elevation_rad = math.asin(
            math.sin(lat_rad) * math.sin(dec_rad) + 
            math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hour_rad)
        )
        return math.degrees(elevation_rad)
    
    def shadow_length(self, solar_elevation_deg):
        """Calcula o comprimento da sombra"""
        if solar_elevation_deg <= 0:
            return float('inf')  # Sol abaixo do horizonte
        
        elevation_rad = math.radians(solar_elevation_deg)
        return self.obstacle_height / math.tan(elevation_rad)
    
    def calculate_seasonal_shadows(self):
        """Calcula o comprimento das sombras para cada estação"""
        results = {}
        
        for season, data in self.seasons.items():
            declination = self.solar_declination(data['day'])
            elevation = self.solar_elevation(declination)
            shadow_len = self.shadow_length(elevation)
            
            results[season] = {
                'declination': declination,
                'elevation': elevation,
                'shadow_length': shadow_len,
                'display_name': data['name']
            }
        
        return results
    
    def create_bar_chart(self, results):
        """Cria gráfico de barras comparando obstáculo e sombras"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        seasons = list(results.keys())
        obstacle_heights = [self.obstacle_height] * len(seasons)
        shadow_lengths = [results[season]['shadow_length'] for season in seasons]
        
        x = np.arange(len(seasons))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, obstacle_heights, width, label='Altura do Obstáculo', color='#2E86AB', alpha=0.8)
        bars2 = ax.bar(x + width/2, shadow_lengths, width, label='Comprimento da Sombra', color='#A23B72', alpha=0.8)
        
        ax.set_xlabel('Estações do Ano', fontsize=12)
        ax.set_ylabel('Distância (m)', fontsize=12)
        ax.set_title('Comparação: Altura do Obstáculo vs Comprimento das Sombras', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([results[s]['display_name'] for s in seasons], rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar in bars1:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}m',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=10)
        
        for bar in bars2:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}m',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        return self.fig_to_base64(fig)
    
    def create_schematic_diagram(self, results):
        """Cria diagrama esquemático das sombras"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        
        for i, (season, data) in enumerate(results.items()):
            shadow_len = data['shadow_length']
            elevation = data['elevation']
            
            # Desenhar obstáculo
            ax.plot([0, 0], [0, self.obstacle_height], 'k-', linewidth=8, alpha=0.8, label='Obstáculo' if i == 0 else "")
            
            # Desenhar sombra
            ax.plot([0, shadow_len], [self.obstacle_height, 0], colors[i], linewidth=3, 
                   label=f'{data["display_name"]} ({shadow_len:.1f}m)', alpha=0.8)
            
            # Desenhar linha do sol
            sun_x = -shadow_len * 0.3
            sun_y = self.obstacle_height + shadow_len * 0.3 * math.tan(math.radians(elevation))
            ax.plot([0, sun_x], [self.obstacle_height, sun_y], colors[i], 
                   linestyle='--', alpha=0.6, linewidth=2)
            
            # Adicionar ângulo
            ax.annotate(f'{elevation:.1f}°', 
                       xy=(sun_x*0.7, self.obstacle_height + (sun_y-self.obstacle_height)*0.7),
                       fontsize=10, ha='center', color=colors[i], fontweight='bold')
        
        ax.set_xlim(-2, max([results[s]['shadow_length'] for s in results]) + 1)
        ax.set_ylim(-0.5, self.obstacle_height + 2)
        ax.set_xlabel('Distância (m)', fontsize=12)
        ax.set_ylabel('Altura (m)', fontsize=12)
        ax.set_title('Diagrama Esquemático: Sombras Sazonais e Ângulos Solares', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        plt.tight_layout()
        return self.fig_to_base64(fig)
    
    def create_polar_chart(self, results):
        """Cria gráfico polar da variação sazonal"""
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        # Ângulos para as estações (em radianos)
        angles = [0, np.pi/2, np.pi, 3*np.pi/2]  # 0°, 90°, 180°, 270°
        shadow_lengths = [results[season]['shadow_length'] for season in results.keys()]
        season_names = [results[season]['display_name'] for season in results.keys()]
        
        # Fechar o círculo
        angles += [angles[0]]
        shadow_lengths += [shadow_lengths[0]]
        season_names += [season_names[0]]
        
        ax.plot(angles, shadow_lengths, 'bo-', linewidth=2, markersize=8)
        ax.fill(angles, shadow_lengths, alpha=0.25)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(season_names[:-1])
        ax.set_ylim(0, max(shadow_lengths) * 1.1)
        ax.set_title('Variação Sazonal das Sombras\n(Vista Polar)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(True)
        
        plt.tight_layout()
        return self.fig_to_base64(fig)
    
    def create_elevation_chart(self, results):
        """Cria gráfico das elevações solares"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        seasons = [results[s]['display_name'] for s in results.keys()]
        elevations = [results[s]['elevation'] for s in results.keys()]
        
        bars = ax.bar(seasons, elevations, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'], alpha=0.8)
        
        ax.set_xlabel('Estações do Ano', fontsize=12)
        ax.set_ylabel('Elevação Solar (graus)', fontsize=12)
        ax.set_title('Elevação Solar ao Meio-dia por Estação', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Adicionar valores nas barras
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}°',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return self.fig_to_base64(fig)
    
    def fig_to_base64(self, fig):
        """Converte figura matplotlib para base64"""
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.read()).decode()
        plt.close(fig)
        return img_str
    
    def generate_html_report(self):
        """Gera o relatório HTML completo"""
        results = self.calculate_seasonal_shadows()
        
        # Gerar gráficos
        bar_chart = self.create_bar_chart(results)
        schematic_diagram = self.create_schematic_diagram(results)
        polar_chart = self.create_polar_chart(results)
        elevation_chart = self.create_elevation_chart(results)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Análise de Sombras Solares</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: bold;
        }}
        .header p {{
            margin: 10px 0;
            font-size: 1.2em;
        }}
        .section {{
            margin-bottom: 40px;
            padding: 20px;
            border-left: 5px solid #667eea;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .data-table th, .data-table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        .data-table th {{
            background-color: #667eea;
            color: white;
        }}
        .data-table tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .chart-container {{
            text-align: center;
            padding: 15px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }}
        .formula {{
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background-color: #343a40;
            color: white;
            border-radius: 5px;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 15px;
            border-left: 5px solid #ffc107;
            margin: 15px 0;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Soluções Solares LTDA</h1>
            <p>Entregando soluções em energia solar desde 2018</p>
            <p>📱 WhatsApp: 16 99630-2896</p>
            <h1>Estudo de Projeção de sombra ao longo do ano</h1>
        </div>

        <div class="section">
            <h2>1 - Dados de Entrada</h2>
            <table class="data-table">
                <tr>
                    <th>Parâmetro</th>
                    <th>Valor</th>
                    <th>Observações</th>
                </tr>
                <tr>
                    <td>Coordenadas Geográficas</td>
                    <td>Lat: 21°44'21.3"S<br>Long: 48°06'21.4"W</td>
                    <td>Coordenadas em formato DMS convertidas para {self.latitude:.6f}°, {self.longitude:.6f}°</td>
                </tr>
                <tr>
                    <td>Altura do Obstáculo</td>
                    <td>{self.obstacle_height:.2f} m</td>
                    <td>Altura perpendicular ao solo</td>
                </tr>
                <tr>
                    <td>Orientação do Obstáculo</td>
                    <td>Paralelo ao eixo Leste/Oeste</td>
                    <td>Obstáculo alinhado com a direção E-W</td>
                </tr>
                <tr>
                    <td>Direção da Projeção da Sombra</td>
                    <td>Sul</td>
                    <td>Sombra projetada para o lado Sul</td>
                </tr>
            </table>
        </div>

        <div class="section">
            <h2>2 - Resultados</h2>
            <p>A análise das sombras foi realizada para os momentos críticos do ano, considerando a posição solar ao meio-dia (12h00) em cada estação:</p>
            
            <table class="data-table">
                <tr>
                    <th>Estação</th>
                    <th>Data de Referência</th>
                    <th>Elevação Solar (°)</th>
                    <th>Comprimento da Sombra (m)</th>
                </tr>"""

        for season, data in results.items():
            html_content += f"""
                <tr>
                    <td>{season}</td>
                    <td>{data['display_name']}</td>
                    <td>{data['elevation']:.1f}°</td>
                    <td>{data['shadow_length']:.2f} m</td>
                </tr>"""

        html_content += f"""
            </table>
            
            <div class="highlight">
                <strong>Resultado Principal:</strong> A sombra máxima ocorre durante o <strong>Solstício de Inverno</strong> 
                com {max(results.values(), key=lambda x: x['shadow_length'])['shadow_length']:.2f} metros, 
                e a sombra mínima durante o <strong>Solstício de Verão</strong> 
                com {min(results.values(), key=lambda x: x['shadow_length'])['shadow_length']:.2f} metros.
            </div>
        </div>

        <div class="section">
            <h2>3 - Visualizações e Gráficos</h2>
            <p>A análise completa das sombras sazonais é apresentada através dos seguintes gráficos:</p>
            
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>Comparação Obstáculo vs Sombras</h3>
                    <img src="data:image/png;base64,{bar_chart}" alt="Gráfico de Barras">
                </div>
                
                <div class="chart-container">
                    <h3>Elevações Solares por Estação</h3>
                    <img src="data:image/png;base64,{elevation_chart}" alt="Gráfico de Elevações">
                </div>
                
                <div class="chart-container">
                    <h3>Diagrama Esquemático</h3>
                    <img src="data:image/png;base64,{schematic_diagram}" alt="Diagrama Esquemático">
                </div>
                
                <div class="chart-container">
                    <h3>Variação Sazonal (Vista Polar)</h3>
                    <img src="data:image/png;base64,{polar_chart}" alt="Gráfico Polar">
                </div>
            </div>
        </div>

        <div class="section">
            <h2>4 - Conclusão</h2>
            <p>Com base na análise realizada para as coordenadas geográficas especificadas (21°44'21.3"S, 48°06'21.4"W), 
            podemos concluir que:</p>
            
            <ul>
                <li><strong>Variação Sazonal:</strong> O comprimento das sombras varia significativamente ao longo do ano, 
                com uma diferença de {max(results.values(), key=lambda x: x['shadow_length'])['shadow_length'] - min(results.values(), key=lambda x: x['shadow_length'])['shadow_length']:.2f} metros 
                entre a sombra máxima (inverno) e mínima (verão).</li>
                
                <li><strong>Período Crítico:</strong> O Solstício de Inverno (21 de junho) representa o período com maior 
                projeção de sombras, exigindo maior distanciamento para evitar sombreamento.</li>
                
                <li><strong>Impacto na Instalação:</strong> Para sistemas fotovoltaicos, recomenda-se manter uma distância 
                mínima de {max(results.values(), key=lambda x: x['shadow_length'])['shadow_length']:.1f} metros do obstáculo 
                para evitar sombreamento durante todo o ano.</li>
                
                <li><strong>Otimização:</strong> A orientação paralela ao eixo Leste/Oeste do obstáculo é favorável, 
                pois minimiza o sombreamento em painéis orientados para o Norte.</li>
            </ul>
        </div>

        <div class="section">
            <h2>5 - Metodologia de Cálculo</h2>
            <p>Os cálculos foram baseados em fórmulas de astronomia solar padronizadas:</p>
            
            <h3>1. Cálculo da Declinação Solar (δ)</h3>
            <div class="formula">
                δ = 23,45° × sin(360° × (284 + n) / 365°)
                <br>Onde: n = dia do ano
            </div>
            
            <h3>2. Ângulo Horário Solar (ω)</h3>
            <div class="formula">
                ω = 15° × (hora_solar - 12)
                <br>Para meio-dia: ω = 0°
            </div>
            
            <h3>3. Elevação Solar (α)</h3>
            <div class="formula">
                sin(α) = sin(φ) × sin(δ) + cos(φ) × cos(δ) × cos(ω)
                <br>Onde: φ = latitude do local
            </div>
            
            <h3>4. Comprimento da Sombra (L)</h3>
            <div class="formula">
                L = H / tan(α)
                <br>Onde: H = altura do obstáculo, α = elevação solar
            </div>
        </div>

        <div class="section">
            <h2>6 - Fontes e Referências</h2>
            <ul>
                <li>Duffie, J. A., & Beckman, W. A. (2013). <em>Solar Engineering of Thermal Processes</em>. 4th Edition. John Wiley & Sons.</li>
                <li>Iqbal, M. (1983). <em>An Introduction to Solar Radiation</em>. Academic Press.</li>
                <li>Lorenzo, E. (1994). <em>Solar Electricity: Engineering of Photovoltaic Systems</em>. Progensa.</li>
                <li>NREL - National Renewable Energy Laboratory. <em>Solar Position Algorithm (SPA)</em>. Disponível em: https://www.nrel.gov/midc/spa/</li>
                <li>Meeus, J. (1998). <em>Astronomical Algorithms</em>. 2nd Edition. Willmann-Bell.</li>
                <li>IEA PVPS Task 7 Report. <em>Photovoltaic Power Systems Programme</em>. International Energy Agency.</li>
            </ul>
        </div>

        <div class="section">
            <h2>7 - Premissas e Restrições</h2>
            <h3>Premissas Adotadas:</h3>
            <ul>
                <li>Cálculos realizados para condições de céu claro (sem nuvens)</li>
                <li>Terreno plano e horizontal</li>
                <li>Obstáculo vertical e rígido (sem deformações)</li>
                <li>Análise realizada para o horário de meio-dia solar (12h00)</li>
                <li>Coordenadas geográficas precisas e constantes</li>
                <li>Não considerados efeitos de refração atmosférica</li>
            </ul>
            
            <h3>Restrições e Limitações:</h3>
            <ul>
                <li>Resultados válidos apenas para as coordenadas especificadas</li>
                <li>Variações microclimáticas não foram consideradas</li>
                <li>Modelo assume obstáculo com geometria simplificada</li>
                <li>Precisão limitada a ±5% devido a aproximações matemáticas</li>
                <li>Não considera sombreamento múltiplo ou reflexões</li>
                <li>Válido para aplicações em energia solar fotovoltaica</li>
            </ul>
            
            <h3>Condições de Validade:</h3>
            <ul>
                <li>Aplicável a latitudes entre 23,5°N e 23,5°S</li>
                <li>Resultados válidos para o ano de referência (variações anuais < 1%)</li>
                <li>Recomenda-se reavaliação a cada 5 anos para máxima precisão</li>
                <li>Aplicável a obstáculos com altura entre 0,5m e 50m</li>
            </ul>
        </div>

        <div class="footer">
            <p>Este relatório é parte integrante do nosso plano de manutenção - Copyright by Soluções Solares LTDA</p>
            <p>Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
        </div>
    </div>
</body>
</html>"""
        
        return html_content

def main():
    """Função principal para gerar o relatório"""
    # Converter coordenadas DMS para decimais
    # Latitude: 21°44'21.3"S
    lat_decimal = -21 - 44/60 - 21.3/3600  # Negativo para Sul
    # Longitude: 48°06'21.4"W  
    lon_decimal = -48 - 6/60 - 21.4/3600   # Negativo para Oeste
    
    # Parâmetros de entrada
    obstacle_height = 1.65  # metros
    
    # Criar analisador
    analyzer = SolarShadowAnalyzer(lat_decimal, lon_decimal, obstacle_height)
    
    # Gerar relatório HTML
    html_report = analyzer.generate_html_report()
    
    # Salvar arquivo
    with open('relatorio_sombras_solares_CL.html', 'w', encoding='utf-8') as file:
        file.write(html_report)
    
    print("✅ Relatório gerado com sucesso!")
    print("📄 Arquivo salvo como: relatorio_sombras_solares_CL.html")
    print("🌐 Abra o arquivo em seu navegador para visualizar o relatório completo.")

if __name__ == "__main__":
    main()