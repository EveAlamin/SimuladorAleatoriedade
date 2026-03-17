import strawberryfields as sf
from strawberryfields.ops import MeasureX
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

NUM_AMOSTRAS = 100000
TITULO_GRAFICO = "Distribuição dos Valores de Quadratura (Vácuo)"


def etapa_1_simulacao_fisica():
    print(f"--- 1. Simulação Física ({NUM_AMOSTRAS} amostras) ---")

    prog = sf.Program(1)
    with prog.context as q:
        MeasureX | q[0]

    eng = sf.Engine("gaussian")
    valores_continuos = np.empty(NUM_AMOSTRAS)

    for i in range(NUM_AMOSTRAS):
        resultado = eng.run(prog)
        valores_continuos[i] = resultado.samples[0][0]
        eng.reset()

    print(f"Primeiras 5 amostras: {valores_continuos[:5]}")
    print(f"Média: {np.mean(valores_continuos):.4f}  |  "
          f"Desvio-padrão: {np.std(valores_continuos):.4f}  |  "
          f"Variância teórica do vácuo: 1.0000")
    return valores_continuos


def etapa_2_processamento(valores_continuos):
    print("\n--- 2. Processamento (Digitalização + Extração de von Neumann) ---")

    bits_brutos = (valores_continuos > 0).astype(int)

    proporcao_uns = np.mean(bits_brutos)
    print(f"Bits brutos — proporção de 1s: {proporcao_uns:.4f} "
          f"(ideal: 0.5000) | viés: {abs(proporcao_uns - 0.5):.4f}")

    bits_extraidos = []
    pares_processados = 0
    pares_descartados = 0

    for i in range(0, len(bits_brutos) - 1, 2):
        b0, b1 = bits_brutos[i], bits_brutos[i + 1]
        pares_processados += 1
        if b0 != b1:
            bits_extraidos.append(b0)
        else:
            pares_descartados += 1

    bits_extraidos = np.array(bits_extraidos)

    proporcao_extraidos = np.mean(bits_extraidos)
    eficiencia = len(bits_extraidos) / pares_processados
    print(f"Bits extraídos: {len(bits_extraidos)} "
          f"(eficiência: {eficiencia:.2%}, pares descartados: {pares_descartados})")
    print(f"Proporção de 1s após extração: {proporcao_extraidos:.4f} "
          f"(viés residual: {abs(proporcao_extraidos - 0.5):.4f})")
    print(f"Primeiros 20 bits: {bits_extraidos[:20]}")

    return bits_extraidos


def etapa_3_validacao_criptografica(chave_bits):
    print("\n--- 3. Validação Criptográfica (Cifra XOR / One-Time Pad) ---")

    mensagem_texto = (
        "Universidade Federal de Uberlândia - Faculdade de Computação (FACOM) 2025. "
        "Este trabalho investiga a geração quântica de números aleatórios (QRNG) "
        "baseada na abordagem de Variáveis Contínuas (CV) em sistemas fotônicos. "
        "A aleatoriedade é extraída das flutuações do vácuo quântico, medidas via "
        "Medição Homódina simulada pela biblioteca Strawberry Fields (Xanadu). "
        "Ao contrário dos métodos de Variáveis Discretas (DV), que dependem de "
        "detectores de fóton único com complexidade de hardware elevada, a abordagem "
        "CV é compatível com componentes ópticos de telecomunicação já consolidados, "
        "oferecendo maior escalabilidade e potencial para taxas de geração de bits "
        "da ordem de gigabits por segundo. Neste pipeline, os valores contínuos "
        "obtidos da simulação são binarizados por limiar e submetidos ao Extrator "
        "de von Neumann, que elimina o viés da fonte de forma incondicional. "
        "A chave resultante é utilizada em uma Cifra XOR (One-Time Pad) para "
        "demonstrar sua aplicabilidade criptográfica. A validade estatística da "
        "chave gerada é avaliada por meio do teste chi-quadrado sobre a distribuição "
        "dos bytes cifrados, exigindo frequência esperada mínima de cinco por célula "
        "para que o teste seja metodologicamente correto. "
        "Iniciação Científica - PROPP UFU - Evellyn Fernanda Alamin Machado e "
        "Giullia Rodrigues. Aleatoriedade Quântica em Sistemas Fotônicos: da "
        "Simulação Computacional à Criptografia Moderna. WTDCC SBC 2025. "
        "Palavras-chave: QRNG, vácuo quântico, variáveis contínuas, criptografia, "
        "Strawberry Fields, extrator de von Neumann, distribuição gaussiana."
    )

    mensagem_bytes = np.frombuffer(mensagem_texto.encode("utf-8"), dtype=np.uint8)
    mensagem_bits  = np.unpackbits(mensagem_bytes)
    tamanho_bits   = len(mensagem_bits)
    tamanho_bytes  = len(mensagem_bytes)

    print(f"Tamanho da mensagem: {tamanho_bytes} bytes ({tamanho_bits} bits)")

    if len(chave_bits) < tamanho_bits:
        raise ValueError(
            f"Chave insuficiente: {len(chave_bits)} bits disponíveis, "
            f"mas a mensagem requer {tamanho_bits} bits."
        )

    chave_utilizada = chave_bits[:tamanho_bits]
    print(f"Taxa de uso da chave: {tamanho_bits / len(chave_bits):.2%}")

    bits_cifrados = np.bitwise_xor(mensagem_bits, chave_utilizada)

    proporcao_uns = np.mean(bits_cifrados)
    print(f"\n[Teste 1] Proporção de 1s nos bits cifrados: {proporcao_uns:.4f} "
          f"(ideal: 0.5000 | desvio: {abs(proporcao_uns - 0.5):.4f})")

    bits_decriptados = np.bitwise_xor(bits_cifrados, chave_utilizada)
    texto_recuperado = np.packbits(bits_decriptados).tobytes().decode("utf-8")

    assert texto_recuperado == mensagem_texto, "ERRO: decriptação falhou!"
    print(f"[Teste 2] Decriptação: bem-sucedida ✓")

    bytes_cifrados = np.packbits(bits_cifrados)
    frequencias    = np.bincount(bytes_cifrados, minlength=256)
    esperado       = tamanho_bytes / 256

    if esperado < 5:
        print(f"[Teste 3] INVÁLIDO — frequência esperada = {esperado:.2f} "
              f"(mínimo exigido: 5).")
        return

    from scipy.stats import chisquare
    chi2, p_valor = chisquare(frequencias)
    print(f"[Teste 3] Chi-quadrado = {chi2:.2f}  |  p-valor = {p_valor:.4f}")
    print(f"          {'Uniforme ✓ (p > 0.05)' if p_valor > 0.05 else 'Não uniforme ✗ (p <= 0.05)'}")

    _plot_distribuicao_bytes(bytes_cifrados, mensagem_bytes, esperado)


def _plot_distribuicao_bytes(bytes_cifrados, bytes_originais, esperado):
    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    fig.suptitle("Validação Criptográfica — Distribuição de Bytes", fontweight="bold")

    freq_orig = np.bincount(bytes_originais, minlength=256)
    freq_cif  = np.bincount(bytes_cifrados,  minlength=256)

    ax1 = axes[0]
    ax1.bar(range(256), freq_orig, color="steelblue", width=1.0)
    ax1.axhline(esperado, color="red", linestyle="--", linewidth=1.2,
                label=f"Esperado uniforme ({esperado:.1f})")
    ax1.set_title("Bytes da mensagem original")
    ax1.set_xlabel("Valor do byte (0–255)")
    ax1.set_ylabel("Frequência")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]
    ax2.bar(range(256), freq_cif, color="darkorange", width=1.0)
    ax2.axhline(esperado, color="red", linestyle="--", linewidth=1.2,
                label=f"Esperado uniforme ({esperado:.1f})")
    ax2.set_title("Bytes cifrados com chave QRNG")
    ax2.set_xlabel("Valor do byte (0–255)")
    ax2.set_ylabel("Frequência")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("validacao_criptografica.png", dpi=150, bbox_inches="tight")
    plt.show()


def validacao_visual(valores_continuos):
    mu_emp  = np.mean(valores_continuos)
    std_emp = np.std(valores_continuos)
    std_teo = 1.0

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(TITULO_GRAFICO, fontsize=13, fontweight="bold")

    ax = axes[0]
    ax.hist(valores_continuos, bins=60, density=True,
            alpha=0.6, color="steelblue", edgecolor="white", label="Dados simulados")

    x = np.linspace(valores_continuos.min(), valores_continuos.max(), 300)

    p_teo = (1 / (np.sqrt(2 * np.pi) * std_teo)) * np.exp(
        -0.5 * ((x - 0) / std_teo) ** 2
    )
    ax.plot(x, p_teo, "r-", linewidth=2, label="Gaussiana teórica (σ=1.000)")

    p_emp = (1 / (np.sqrt(2 * np.pi) * std_emp)) * np.exp(
        -0.5 * ((x - mu_emp) / std_emp) ** 2
    )
    ax.plot(x, p_emp, "g--", linewidth=1.5,
            label=f"Ajuste empírico (μ={mu_emp:.3f}, σ={std_emp:.3f})")

    ax.set_xlabel("Valor da Quadratura q")
    ax.set_ylabel("Densidade de Probabilidade")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_title("Distribuição Gaussiana do Vácuo")

    from scipy import stats
    ax2 = axes[1]
    (osm, osr), (slope, intercept, r) = stats.probplot(valores_continuos, dist="norm")
    ax2.scatter(osm, osr, s=1, alpha=0.3, color="steelblue")
    ax2.plot(osm, slope * np.array(osm) + intercept, "r-", linewidth=1.5,
             label=f"Linha de referência (R²={r**2:.5f})")
    ax2.set_xlabel("Quantis teóricos")
    ax2.set_ylabel("Quantis observados")
    ax2.set_title("Q-Q Plot (validação de normalidade)")
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("validacao_gaussiana.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("\nGráfico salvo em 'validacao_gaussiana.png'")


if __name__ == "__main__":
    dados_vacuo = etapa_1_simulacao_fisica()
    validacao_visual(dados_vacuo)
    chave_aleatoria = etapa_2_processamento(dados_vacuo)
    etapa_3_validacao_criptografica(chave_aleatoria)