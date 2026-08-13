"""Cálculo determinístico da tabela RTE Rodonaves extraída do Excel."""

from __future__ import annotations

import math
import re
import unicodedata


class CalculoRodonavesError(ValueError):
    pass


def _cep(valor: str | None) -> int:
    digitos = re.sub(r"\D", "", valor or "")
    if len(digitos) != 8:
        raise CalculoRodonavesError("CEP de destino inválido ou ausente")
    return int(digitos)


def _buscar_faixa(lista: list[dict], cep: int) -> dict | None:
    return next((item for item in lista if item["cep_inicio"] <= cep <= item["cep_fim"]), None)


def _normalizar_texto(valor: str | None) -> str:
    texto = unicodedata.normalize("NFKD", valor or "")
    return " ".join("".join(c for c in texto if not unicodedata.combining(c)).upper().split())


def _aliquota_icms(regras: dict, origem_uf: str, destino_uf: str) -> float:
    configuracao = regras.get("icms")
    if not configuracao or not origem_uf or not destino_uf:
        return 0.0
    if origem_uf in configuracao["origens_reduzida"] and destino_uf in configuracao["destinos_reduzida"]:
        return float(configuracao["aliquota_reduzida"])
    return float(configuracao["aliquota_padrao"])


def calcular_rodonaves(dados: dict, cotacao: dict) -> dict:
    cep = _cep(cotacao.get("destino_cep"))
    cobertura = _buscar_faixa(dados["coberturas"], cep)
    if not cobertura:
        raise CalculoRodonavesError("CEP de destino não atendido pela malha importada")

    peso_real = float(cotacao.get("peso") or 0)
    volume_m3 = float(cotacao.get("volume_total_m3") or 0)
    peso_cubado = volume_m3 * float(dados["fator_cubagem"])
    peso = max(peso_real, peso_cubado)
    if peso <= 0:
        raise CalculoRodonavesError("Peso deve ser maior que zero")
    if peso > float(dados["peso_limite_kg"]):
        raise CalculoRodonavesError("Peso acima do limite LTL de 7.000 kg; cotação deve ser consultada")

    km = max(1, int(cobertura["km"]))
    faixa = next(
        (item for item in dados["matriz_tarifas"] if km >= item["km_min"] and (item["km_max"] is None or km <= item["km_max"])),
        None,
    )
    if not faixa:
        raise CalculoRodonavesError(f"Não existe tarifa para a distância de {km} km")
    if peso <= 10:
        frete_peso = faixa["ate_10"]
    elif peso <= 20:
        frete_peso = faixa["ate_20"]
    elif peso <= 40:
        frete_peso = faixa["ate_40"]
    elif peso <= 60:
        frete_peso = faixa["ate_60"]
    elif peso <= 100:
        frete_peso = faixa["ate_100"]
    else:
        frete_peso = peso * faixa["por_kg_acima_100"]

    regras = dados["regras"]
    valor_nf = float(cotacao.get("valor_nf") or 0)
    frete_valor = max(valor_nf * regras["frete_valor_percentual"], regras["frete_valor_minimo"])
    uf = cobertura["uf"]
    grupo_sul_sudeste = {"RS", "SC", "PR", "SP", "MG", "GO", "DF"}
    if uf in grupo_sul_sudeste:
        percentual = regras["gris_sul_sudeste_percentual_ate_10k"] if valor_nf <= 10000 else regras["gris_sul_sudeste_percentual_acima_10k"]
        gris = max(valor_nf * percentual, regras["gris_sul_sudeste_minimo"])
    else:
        gris = max(valor_nf * regras["gris_demais_percentual"], regras["gris_demais_minimo"])
    pedagio = math.ceil(peso / 100) * regras["pedagio_por_100kg"]
    taxa_destino = float(cobertura["taxa_final"])
    cidade = _normalizar_texto(cobertura["cidade"])
    for taxa_especial in regras.get("taxas_entrega_por_peso", []):
        if cidade in taxa_especial["cidades"]:
            taxa_destino = float(
                taxa_especial["ate_limite"]
                if peso <= float(taxa_especial["peso_limite"])
                else taxa_especial["acima_limite"]
            )
            break

    origem_uf = str(cotacao.get("origem_uf") or "").upper()
    taxa_administrativa = 0.0
    regra_tas = regras.get("taxa_administrativa")
    if regra_tas and (origem_uf in regra_tas["ufs"] or uf in regra_tas["ufs"]):
        taxa_administrativa = float(regra_tas["valor"])

    taxas_cep = []
    restricao = _buscar_faixa(dados["zonas"]["restricao_rj"], cep)
    if restricao:
        taxas_cep.append({"nome": "Zona de restrição RJ", "valor": restricao["valor"]})
    risco = _buscar_faixa(dados["zonas"]["risco_sp"], cep)
    if risco:
        taxas_cep.append({"nome": "Zona de risco SP", "valor": risco["valor"]})
    if cep in set(dados["zonas"]["centro_expandido_sp"]):
        centro = next((item for item in regras["centro_sp_faixas"] if peso <= item["peso_max"]), None)
        if not centro:
            raise CalculoRodonavesError("Carga acima de 1.500 kg para o centro expandido de SP exige consulta")
        taxas_cep.append({"nome": "Centro expandido SP", "valor": centro["valor"]})

    detalhadas = [
        {"nome": "Frete peso", "valor": frete_peso},
        {"nome": "Frete valor", "valor": frete_valor},
        {"nome": "GRIS", "valor": gris},
        {"nome": "Pedágio", "valor": pedagio},
        {"nome": "Taxas do destino", "valor": taxa_destino},
        {"nome": "TAS", "valor": taxa_administrativa},
        *taxas_cep,
    ]
    subtotal = sum(float(item["valor"]) for item in detalhadas)
    aliquota_icms = _aliquota_icms(regras, origem_uf, uf)
    total_com_imposto = subtotal / (1 - aliquota_icms) if aliquota_icms else subtotal
    if aliquota_icms:
        detalhadas.append({
            "nome": f"ICMS ({aliquota_icms * 100:g}% por dentro)",
            "valor": total_com_imposto - subtotal,
        })
    total = round(total_com_imposto, 2)
    return {
        "status": "success", "valor_total": total, "prazo_dias": int(cobertura["prazo_pj"]),
        "peso_considerado_kg": round(peso, 3), "peso_real_kg": peso_real, "peso_cubado_kg": round(peso_cubado, 3),
        "taxas_detalhadas": [{**item, "valor": round(float(item["valor"]), 2)} for item in detalhadas],
        "detalhe_calculo": {
            "cep": f"{cep:08d}", "cidade": cobertura["cidade"], "uf": uf, "distancia_km": km,
            "faixa_km": faixa["descricao"], "prazo_base": "PJ em dias úteis",
            "impostos_inclusos": bool(aliquota_icms), "aliquota_icms": aliquota_icms,
            "observacao_impostos": "ICMS calculado por dentro conforme origem e destino" if aliquota_icms else "Imposto não calculado por falta de UF",
        },
    }
