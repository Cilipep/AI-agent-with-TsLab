from jinja2 import Template


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Chart Analysis: {{ symbol }} ({{ interval }})</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #0d1117; color: #c9d1d9; }
  h1 { color: #58a6ff; border-bottom: 1px solid #21262d; padding-bottom: 10px; }
  h2 { color: #79c0ff; margin-top: 30px; }
  .card { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 16px; margin: 12px 0; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; }
  .metric { text-align: center; padding: 12px; }
  .metric .value { font-size: 24px; font-weight: bold; }
  .metric .label { color: #8b949e; font-size: 13px; }
  .bullish { color: #3fb950; }
  .bearish { color: #f85149; }
  .neutral { color: #d29922; }
  table { width: 100%; border-collapse: collapse; margin: 10px 0; }
  th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #21262d; }
  th { background: #1c2128; color: #8b949e; font-weight: 600; }
  tr:hover { background: #1c2128; }
  .signal-bullish { color: #3fb950; }
  .signal-bearish { color: #f85149; }
  .signal-neutral { color: #d29922; }
  .footer { margin-top: 40px; padding-top: 16px; border-top: 1px solid #21262d; color: #484f58; font-size: 12px; }
</style>
</head>
<body>

<h1>{{ symbol }} &mdash; Анализ графика ({{ interval }})</h1>
<p style="color:#8b949e;">{{ exchange }} | {{ timestamp }} | Последняя цена: <strong>{{ "{:.8f}".format(price) }}</strong></p>

<h2>Тренд и индикаторы</h2>
<div class="grid">
  <div class="card metric">
    <div class="label">Тренд</div>
    <div class="value {{ 'bullish' if 'бычий' in trend.trend.lower() or 'восходящий' in trend.trend.lower() else 'bearish' if 'медвежий' in trend.trend.lower() or 'нисходящий' in trend.trend.lower() else 'neutral' }}">{{ trend.trend }}</div>
  </div>
  <div class="card metric">
    <div class="label">Моментум (RSI)</div>
    <div class="value {{ 'bullish' if trend.momentum in ['Бычий'] else 'bearish' if trend.momentum in ['Медвежий'] else 'neutral' }}">{{ trend.rsi }}</div>
    <div class="label">{{ trend.momentum }}</div>
  </div>
  <div class="card metric">
    <div class="label">MACD</div>
    <div class="value {{ 'bullish' if 'бычий' in trend.macd_signal.lower() else 'bearish' if 'медвежий' in trend.macd_signal.lower() else 'neutral' }}">{{ trend.macd_signal }}</div>
  </div>
  <div class="card metric">
    <div class="label">ATR</div>
    <div class="value">{{ trend.atr }}</div>
    <div class="label">Волатильность</div>
  </div>
</div>

<div class="card">
  <table>
    <tr><td>Цена vs EMA21</td><td class="{{ 'bullish' if '+' in trend.price_vs_ema21 else 'bearish' }}">{{ trend.price_vs_ema21 }}</td></tr>
    <tr><td>Цена vs EMA50</td><td class="{{ 'bullish' if '+' in trend.price_vs_ema50 else 'bearish' }}">{{ trend.price_vs_ema50 }}</td></tr>
  </table>
</div>

<h2>Объём</h2>
<div class="grid">
  <div class="card metric">
    <div class="label">Текущий объём</div>
    <div class="value">{{ volume.last_volume }}</div>
  </div>
  <div class="card metric">
    <div class="label">Средний объём</div>
    <div class="value">{{ volume.avg_volume }}</div>
  </div>
  <div class="card metric">
    <div class="label">Отношение к среднему</div>
    <div class="value {{ 'bullish' if volume.volume_ratio > 1.5 else 'bearish' if volume.volume_ratio < 0.8 else 'neutral' }}">{{ volume.volume_ratio }}x</div>
    <div class="label">{{ volume.volume_status }}</div>
  </div>
  <div class="card metric">
    <div class="label">OBV тренд</div>
    <div class="value {{ 'bullish' if 'Восходящий' in volume.obv_trend else 'bearish' }}">{{ volume.obv_trend }}</div>
  </div>
</div>

{% if volume.spikes %}
<h3>Всплески объёма</h3>
<table>
  <tr><th>Время</th><th>Объём</th><th>Отношение</th><th>Направление</th></tr>
  {% for spike in volume.spikes %}
  <tr>
    <td>{{ spike.timestamp }}</td>
    <td>{{ spike.volume }}</td>
    <td>{{ spike.ratio }}x</td>
    <td class="{{ 'signal-bullish' if spike.direction == 'buy' else 'signal-bearish' }}">{{ 'Покупка' if spike.direction == 'buy' else 'Продажа' }}</td>
  </tr>
  {% endfor %}
</table>
{% endif %}

<h2>Уровни поддержки / сопротивления</h2>
<div class="grid">
  <div class="card">
    <h3 class="bullish">Поддержка</h3>
    {% if levels.support %}
    <table>
      <tr><th>Уровень</th><th>Касаний</th><th>Расстояние</th></tr>
      {% for l in levels.support %}
      <tr><td>{{ l.price }}</td><td>{{ l.touches }}</td><td>-{{ l.distance }}</td></tr>
      {% endfor %}
    </table>
    {% else %}
    <p style="color:#8b949e;">Не найдено</p>
    {% endif %}
  </div>
  <div class="card">
    <h3 class="bearish">Сопротивление</h3>
    {% if levels.resistance %}
    <table>
      <tr><th>Уровень</th><th>Касаний</th><th>Расстояние</th></tr>
      {% for l in levels.resistance %}
      <tr><td>{{ l.price }}</td><td>{{ l.touches }}</td><td>+{{ l.distance }}</td></tr>
      {% endfor %}
    </table>
    {% else %}
    <p style="color:#8b949e;">Не найдено</p>
    {% endif %}
  </div>
</div>

<h2>Свечные паттерны (последние 20 свечей)</h2>
{% set ns = namespace(found=false) %}
<table>
  <tr><th>Время</th><th>Паттерн</th><th>Сигнал</th></tr>
  {% for p in patterns %}
  {% if p.pattern %}
  {% set ns.found = true %}
  <tr>
    <td>{{ p.timestamp }}</td>
    <td>{{ p.pattern }}</td>
    <td class="{{ 'signal-bullish' if 'бычий' in p.signal.lower() else 'signal-bearish' if 'медвежий' in p.signal.lower() else 'signal-neutral' }}">
      {{ p.signal }}
    </td>
  </tr>
  {% endif %}
  {% endfor %}
</table>
{% if not ns.found %}
<p style="color:#8b949e;">Сигнальных паттернов не обнаружено</p>
{% endif %}

<div class="footer">
  Chart Analyzer | {{ exchange }} | {{ timestamp }}
</div>

</body>
</html>"""

_df_timestamps = None


def set_timestamps(ts):
    global _df_timestamps
    _df_timestamps = ts


def render_report(symbol, interval, exchange, timestamp, price, trend, volume, levels, patterns_data):
    tpl = Template(HTML_TEMPLATE)

    pattern_rows = []
    for idx, row in patterns_data.iterrows():
        if row["pattern"]:
            pattern_rows.append({
                "timestamp": str(_df_timestamps.get(idx, "")) if _df_timestamps is not None else "",
                "pattern": row["pattern"],
                "signal": row["signal"],
            })

    return tpl.render(
        symbol=symbol,
        interval=interval,
        exchange=exchange,
        timestamp=timestamp,
        price=price,
        trend=trend,
        volume=volume,
        levels=levels,
        patterns=pattern_rows,
    )
