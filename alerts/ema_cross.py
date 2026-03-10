# ema_cross.py

previous_states = {}

def get_state(a, b):
    if a > b:
        return "bullish"
    return "bearish"


def detect_cross(symbol, name, value_a, value_b):
    global previous_states

    key = f"{symbol}_{name}"
    state = get_state(value_a, value_b)

    signal = None

    if key in previous_states:
        if state != previous_states[key]:
            signal = state

    previous_states[key] = state

    return signal


def check_ema_cross(symbol, ema_values):
    """
    ema_values = {
        "short": 12.5,
        "mid": 11.9,
        "long": 11.2
    }
    """

    signals = []

    ema_short = ema_values.get("short")
    ema_mid = ema_values.get("mid")
    ema_long = ema_values.get("long")

    # short vs mid
    if ema_short is not None and ema_mid is not None:
        cross = detect_cross(symbol, "short_mid", ema_short, ema_mid)
        if cross:
            signals.append({
                "type": "short_mid",
                "signal": cross
            })

    # mid vs long
    if ema_mid is not None and ema_long is not None:
        cross = detect_cross(symbol, "mid_long", ema_mid, ema_long)
        if cross:
            signals.append({
                "type": "mid_long",
                "signal": cross
            })

    # short vs long
    if ema_short is not None and ema_long is not None:
        cross = detect_cross(symbol, "short_long", ema_short, ema_long)
        if cross:
            signals.append({
                "type": "short_long",
                "signal": cross
            })

    return signals