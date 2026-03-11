import multiprocessing
import pandas as pd

import history_manager

def _run_tv_window(symbol, emas):
    from lightweight_charts import Chart
    chart = Chart(toolbox=True, width=800, height=480)
    
    chart.layout(background_color='#141414', text_color='#FFFFFF')
    chart.candle_style(up_color='#00E676', down_color='#FF5252', wick_up_color='#00E676', wick_down_color='#FF5252')
    chart.grid(vert_enabled=False, horz_enabled=False)
    chart.legend(visible=True)

    ema_lines = []
    colors = ['#29B6F6', '#FFA726', '#EF5350', '#AB47BC', '#26A69A']
    for i, period in enumerate(emas):
        line = chart.create_line(name=f'EMA {period}', color=colors[i % len(colors)])
        ema_lines.append((period, line))

    # ✅ ใหม่: line series สำหรับโหมด Line Chart
    price_line = chart.create_line(name='Price', color='#00E676', width=2)

    # ติดตามสถานะปัจจุบัน
    current_interval = ['1h']
    current_type = ['candle']  # ใช้ list เพื่อแก้ค่าใน closure ได้

    def update_chart(c, interval):
        df = history_manager.update_and_get_data(symbol, interval)
        if df is None or df.empty:
            return

        if current_type[0] == 'candle':
            c.set(df)
            price_line.set(pd.DataFrame())  # ซ่อนเส้น
        else:
            c.set(pd.DataFrame())  # ซ่อนแท่งเทียน
            line_df = pd.DataFrame({'time': df['date'], 'Price': df['close']})
            price_line.set(line_df)

        # วาดเส้น EMA ทั้งสองโหมด
        for period, line in ema_lines:
            if period < len(df):
                ema_series = df['close'].ewm(span=period, adjust=False).mean()
                ema_df = pd.DataFrame({'time': df['date'], f'EMA {period}': ema_series})
                line.set(ema_df)

    # ✅ ใหม่: ปุ่มสลับ Candle / Line
    def switch_candle(c):
        current_type[0] = 'candle'
        update_chart(c, current_interval[0])

    def switch_line(c):
        current_type[0] = 'line'
        update_chart(c, current_interval[0])

    # ปุ่ม Timeframe (แก้ closure bug ด้วย default argument)
    def make_tf(iv):
        def fn(c):
            current_interval[0] = iv
            update_chart(c, iv)
        return fn

    chart.topbar.button('btn_1m',  '1M',  func=make_tf('1m'))
    chart.topbar.button('btn_5m',  '5M',  func=make_tf('5m'))
    chart.topbar.button('btn_15m', '15M', func=make_tf('15m'))
    chart.topbar.button('btn_1h',  '1H',  func=make_tf('1h'))
    chart.topbar.button('btn_4h',  '4H',  func=make_tf('4h'))
    chart.topbar.button('btn_1d',  '1D',  func=make_tf('1d'))

    # ✅ ปุ่มสลับกราฟ
    chart.topbar.button('btn_candle', '🕯 Candle', func=switch_candle)
    chart.topbar.button('btn_line',   '📈 Line',   func=switch_line)

    update_chart(chart, '1h')
    chart.show(block=True)

def show_interactive_chart(symbol, emas):
    p = multiprocessing.Process(target=_run_tv_window, args=(symbol, emas))
    p.start()