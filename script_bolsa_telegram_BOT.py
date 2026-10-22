import datetime
import requests
import yfinance as yf

# --- As suas credenciais do Telegram ---
TELEGRAM_TOKEN = "8974406738:AAETB8ZCo8Vq0-nJ3Wmk702q5WBWaOO4P-U"
CHAT_ID = "6128342566"


def enviar_alerta_telegram(mensagem):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f"Erro ao enviar mensagem para o Telegram: {e}")


# --- Universo Organizado por Setores ---
SETORES = {
    "Semicondutores": ["SMH", "NVDA", "ASML", "TSM", "AVGO"],
    "Robótica & Automação": ["BOTZ", "ISRG", "FANUY"],
    "Energia Limpa & Nuclear": ["URA", "CCJ", "TAN", "ENPH", "NLR"],
}


def analisar_mercado_setorial():
  print("A iniciar a análise setorial de mercado...")
  alertas = []

  for setor, tickers in SETORES.items():
    for ticker in tickers:
      try:
        print(f"A analisar {ticker} ({setor})...")
        stock = yf.Ticker(ticker)
        dados = stock.history(period="1y")
        info = stock.info

        if dados.empty or len(dados) < 20:
          continue

        # 1. Filtro Fundamental Básico (Exemplo: Capitalização > 1.500M USD)
        market_cap = info.get("marketCap", 0)
        if market_cap and market_cap < 1500000000:
          continue

        # 2. Variação Pontual (última sessão)
        preco_ontem = dados["Close"].iloc[-2]
        preco_hoje = dados["Close"].iloc[-1]
        variacao_diaria = ((preco_hoje - preco_ontem) / preco_ontem) * 100

        # Média de volume recente (20 dias)
        volume_medio = dados["Volume"].rolling(window=20).mean().iloc[-1]
        volume_hoje = dados["Volume"].iloc[-1]

        # Critérios de Alerta: Queda forte (> 5%) ou Breakout de alta (> 4% com volume)
        if variacao_diaria <= -5.0:
          alertas.append(
              f"📉 *ALERTA DE QUEDA (Oportunidade?)*\n"
              f"🏷 *Setor:* {setor}\n"
              f"📈 *Ativo:* `{ticker}`\n"
              f"💵 *Preço:* ${preco_hoje:.2f} (`{variacao_diaria:.1f}%`)\n"
          )
        elif variacao_diaria >= 4.0 and volume_hoje > (1.5 * volume_medio):
          alertas.append(
              f"🚀 *ALERTA DE MOMENTUM / BREAKOUT*\n"
              f"🏷 *Setor:* {setor}\n"
              f"📈 *Ativo:* `{ticker}`\n"
              f"💵 *Preço:* ${preco_hoje:.2f} (`+{variacao_diaria:.1f}%`)\n"
              f"📊 *Volume:* Acima da média\n"
          )

      except Exception as e:
        print(f"Erro ao processar {ticker}: {e}")

  # Enviar mensagens consolidadas para o Telegram (se existirem alertas)
  if alertas:
    mensagem_final = (
        f"🔔 *RELATÓRIO DE ALERTAS SETORIAIS*\n"
        f"📅 _{datetime.date.today()}_\n\n" + "\n---\n".join(alertas)
    )
    enviar_alerta_telegram(mensagem_final)
    print("Relatório enviado com sucesso para o Telegram!")
  else:
    print(
        "Análise concluída. Nenhum ativo atingiu os critérios de alerta hoje."
    )


if __name__ == "__main__":
  analisar_mercado_setorial()
  
  
  import time

# Intervalo de execução (exemplo: a cada 6 horas)
INTERVALO_HORAS = 6

print(
    f"Bot em modo contínuo. Vai verificar o mercado a cada"
    f" {INTERVALO_HORAS} horas..."
)

while True:
  try:
    # Executa a sua função principal definida anteriormente
    analisar_mercado_setorial()
  except Exception as e:
    print(f"Erro no ciclo: {e}")

  # Espera o tempo definido (convertido para segundos)
  time.sleep(INTERVALO_HORAS * 3600)
