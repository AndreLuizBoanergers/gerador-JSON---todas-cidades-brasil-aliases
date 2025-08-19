
import csv
import json

# ===================================
# 1. Ler estados.csv e criar mapa UF -> Nome do Estado
# ===================================
estados = {}  # ex: {"SP": "São Paulo", "RJ": "Rio de Janeiro"}

with open('estados.csv', mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        uf = row['UF'].strip()
        estado = row['Estado'].strip()
        estados[uf] = estado

print(f"✅ {len(estados)} estados carregados")

# ===================================
# 2. Ler municipios.csv e gerar cidades.json
# ===================================
cidades = []

# Abre o CSV com delimitador ;
with open('municipios.csv', mode='r', encoding='utf-8') as f:
    # Vamos ler manualmente porque o cabeçalho pode estar fora do padrão
    linhas = f.readlines()

for linha in linhas:
    linha = linha.strip()
    if not linha or linha.startswith('IBGE') or linha.startswith('UF'):
        continue  # pula cabeçalho

    partes = linha.split(';')
    if len(partes) < 8:
        continue

    try:
        # Ajuste conforme seu formato
        # Exemplo: RO;Alta Floresta D'oeste;110001;1100015;RO;Alta Floresta D'oeste;Região Norte;24392;Pequeno II
        if len(partes[0]) == 2:  # começa com UF
            uf = partes[0]
            municipio = partes[1]
            ibge = partes[2]
            ibge7 = partes[3]
            regiao = partes[6]
            populacao = int(partes[7]) if partes[7].isdigit() else 0
            porte = partes[8] if len(partes) > 8 else ""
        else:
            # Formato: ROAlta Floresta;110001;...
            codigo = partes[0]
            uf = codigo[:2]
            municipio = codigo[2:]
            ibge = partes[1]
            ibge7 = partes[2]
            regiao = partes[5]
            populacao = int(partes[6]) if partes[6].isdigit() else 0
            porte = partes[7] if len(partes) > 7 else ""

        # Nome do estado completo
        estado_nome = estados.get(uf, uf)

        # Gera aliases para busca inteligente
        def remover_acentos(texto):
            import unicodedata
            return ''.join(c for c in unicodedata.normalize('NFD', texto) if ord(c) < 128)

        texto_sem_acento = remover_acentos(municipio.lower())
        alias = [
            municipio.lower(),
            texto_sem_acento,
            uf.lower(),
            uf,
            f"{municipio.lower()} {uf.lower()}",
            f"{texto_sem_acento} {uf.lower()}",
            municipio.lower().replace(' ', ''),
            texto_sem_acento.replace(' ', ''),
        ]

        # Abreviações comuns
        if 'sao' in texto_sem_acento or 'são' in texto_sem_acento:
            sigla = ''.join([p[0] for p in texto_sem_acento.split()])
            alias.append(sigla)
            alias.append(texto_sem_acento[:8])  # prefixo

        alias = list(set(alias))  # remove duplicatas

        cidades.append({
            "municipio": municipio,
            "uf": uf,
            "estado": estado_nome,
            "regiao": regiao,
            "ibge": ibge,
            "ibge7": ibge7,
            "populacao": populacao,
            "porte": porte,
            "capital": "Capital" in porte or "capital" in porte,
            "alias": alias
        })

    except Exception as e:
        print("Erro processando linha:", linha[:50], "...", e)
        continue

# ===================================
# 3. Salvar como cidades.json
# ===================================
with open('cidades.json', 'w', encoding='utf-8') as f:
    json.dump(cidades, f, ensure_ascii=False, indent=2)

print(f"✅ Arquivo 'cidades.json' gerado com {len(cidades)} municípios!")
