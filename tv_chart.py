import multiprocessing
import pandas as pd
from lightweight_charts import Chart
import history_manager # ✅ เรียกใช้งานตัวจัดการ CSV ของเรา

def _run_tv_window(symbol, emas):
    chart = Chart(toolbox=True, width=1000, height=600)
    
    chart.layout(background_color='#141414', text_color='#FFFFFF')
    chart.candle_style(up_color='#00E676', down_color='#FF5252', wick_up_color='#00E676', wick_down_color='#FF5252')
    chart.grid(vert_enabled=False, horz_enabled=False)
    chart.legend(visible=True)

    ema_lines = []
    colors = ['#29B6F6', '#FFA726', '#EF5350', '#AB47BC', '#26A69A']
    for i, period in enumerate(emas):
        line = chart.create_line(name=f'EMA {period}', color=colors[i % len(colors)])
        ema_lines.append((period, line))

    def update_chart(c, interval):
        # 🚀 แก้ไขตรงนี้: เปลี่ยนมาเรียกใช้ history_manager แทน get_binance_data
        df = history_manager.update_and_get_data(symbol, interval)
        
        if df is None or df.empty: 
            return
            
        c.set(df) 
        
        for period, line in ema_lines:
            if period < len(df):
                ema_series = df['close'].ewm(span=period, adjust=False).mean()
                line_df = pd.DataFrame({'time': df['date'], f'EMA {period}': ema_series})
                line.set(line_df)

    # ปุ่มเปลี่ยน Timeframe บนกราฟ
    chart.topbar.button('btn_1m', '1M', func=lambda c: update_chart(c, '1m'))
    chart.topbar.button('btn_5m', '5M', func=lambda c: update_chart(c, '5m'))
    chart.topbar.button('btn_15m', '15M', func=lambda c: update_chart(c, '15m'))
    chart.topbar.button('btn_1h', '1H', func=lambda c: update_chart(c, '1h'))
    chart.topbar.button('btn_4h', '4H', func=lambda c: update_chart(c, '4h'))
    chart.topbar.button('btn_1d', '1D', func=lambda c: update_chart(c, '1d'))

    update_chart(chart, '1h')
    chart.show(block=True)

def show_interactive_chart(symbol, emas):
    p = multiprocessing.Process(target=_run_tv_window, args=(symbol, emas))
    p.start()