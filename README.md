# QRNG Fotônico — Simulação de Aleatoriedade Quântica

Simulação computacional de um Gerador Quântico de Números Aleatórios (QRNG) baseado em sistemas fotônicos de Variáveis Contínuas (CV). A aleatoriedade é extraída das flutuações do vácuo quântico via Medição Homódina, utilizando o formalismo gaussiano do Strawberry Fields.

> Trabalho vinculado ao artigo *"Aleatoriedade Quântica em Sistemas Fotônicos: da Simulação Computacional à Criptografia Moderna"* — WTDCC SBC 2025 — UFU/FACOM.

---

## Resultados

**Validação da fonte física (100.000 amostras)**
| Parâmetro | Teórico | Empírico | Desvio |
|-----------|---------|----------|--------|
| Média (µ) | 0,0000 | −0,0038 | −0,004 |
| Desvio-padrão (σ) | 1,0000 | 0,9981 | −0,002 |
| R² (Q-Q plot) | — | 0,99998 | — |

**Extração de von Neumann**
| Métrica | Valor |
|---------|-------|
| Bits extraídos | 25.020 |
| Eficiência do extrator | 50,04% |
| Eficiência teórica esperada | 50,00% |
| Proporção de 1s | 0,4954 |
| Viés residual | −0,46% |
| IC 95% do viés residual | [−1,08%; +0,16%] |

**Validação criptográfica (One-Time Pad, 1.612 bytes)**
| Teste | Resultado |
|-------|-----------|
| Decriptação | ✓ 100% de fidelidade |
| Proporção de 1s cifrados | 0,5053 |
| Chi-quadrado (χ²) | 254,32 (255 graus de liberdade) |
| p-valor | 0,5002 — Uniforme ✓ |

---

## Pipeline
```
Vácuo Quântico → Medição Homódina → Binarização por Limiar → Extrator de von Neumann → Chave → Cifra XOR (OTP)
```

---

## Frameworks e Tecnologias

![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=flat&logo=python&logoColor=white)
![StrawberryFields](https://img.shields.io/badge/Strawberry_Fields_0.23-FF69B4?style=flat&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy_1.26-013243?style=flat&logo=numpy&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy_1.12-8CAAE6?style=flat&logo=scipy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat&logoColor=white)

---

## Instalação
```bash
pip install strawberryfields numpy matplotlib scipy
```

## Como rodar
```bash
python qrng_simulacao.py
```

Serão gerados automaticamente:
- `validacao_gaussiana.png` — histograma com curva teórica + Q-Q plot (R² = 0,99998)
- `validacao_criptografica.png` — distribuição de bytes originais vs. cifrados

---

## Observação

Os resultados derivam de uma simulação clássica do formalismo gaussiano, não de um experimento físico real. O backend do Strawberry Fields reproduz fielmente a estatística das flutuações do vácuo quântico, mas não captura imperfeições de implementações físicas como ruído de detecção e perdas ópticas. Os resultados representam um limite superior de desempenho.
