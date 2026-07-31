"""
Styling for the Groww AI assistant shell.

Streamlit gives widgets no styling hooks of their own, so groups of buttons are
targeted by emitting a marker element and styling the block that follows it.
"""

GROWW_GREEN = "#00b386"

STYLES = f"""
<style>
    /* ---------- Streamlit chrome ---------- */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding: 1.5rem 2.5rem 3rem; max-width: 1080px; }}
    section[data-testid="stSidebar"] {{
        background: #f1f8f5;
        border-right: 1px solid #e2ece7;
        width: 272px !important;
    }}
    section[data-testid="stSidebar"] .block-container {{ padding: 1.25rem 1rem; }}
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{ gap: 0.1rem; }}
    .element-container:has(.gw-mark) {{ display: none; }}

    /* ---------- Sidebar ---------- */
    .gw-brand {{
        display: flex; align-items: center; gap: 0.6rem;
        margin: 0.2rem 0 1rem 0.15rem;
    }}
    .gw-brand-mark {{
        width: 32px; height: 32px; border-radius: 50%;
        background: conic-gradient(from 210deg, #5b8def, #00b386, #7c3aed, #5b8def);
    }}
    .gw-brand-name {{ font-size: 1.15rem; font-weight: 700; color: #111827; }}
    .gw-brand-name span {{ color: {GROWW_GREEN}; }}

    .gw-side-label {{
        font-size: 0.78rem; font-weight: 700; color: #374151;
        margin: 0.9rem 0 0.15rem 0.15rem; padding-bottom: 0.5rem;
    }}
    .gw-side-rule {{ border-top: 1px solid #e2ece7; margin: 0.9rem 0 0.35rem; }}
    .gw-nav {{
        display: flex; align-items: center; gap: 0.55rem;
        padding: 0.42rem 0.55rem; font-size: 0.85rem; color: #374151;
    }}
    .gw-nav .gw-nav-icon {{ color: #9aa8a2; width: 14px; }}
    .gw-nav .gw-nav-badge {{ font-size: 0.72rem; color: #6b7280; }}

    /* Sidebar buttons double as nav rows */
    section[data-testid="stSidebar"] .stButton > button {{
        width: 100%; justify-content: flex-start;
        background: transparent; border: none; color: #374151;
        padding: 0.42rem 0.55rem; border-radius: 8px; min-height: 0;
    }}
    section[data-testid="stSidebar"] .stButton > button p {{
        font-size: 0.85rem; font-weight: 500; text-align: left;
        line-height: 1.35; margin: 0;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: #e4f1eb; color: #111827;
    }}
    .element-container:has(.gw-mark-newchat) + .element-container button {{
        border: 1px solid #b9dfd0 !important; background: #ffffff !important;
        justify-content: center !important; margin-bottom: 0.35rem;
    }}
    .element-container:has(.gw-mark-newchat) + .element-container button p {{
        color: {GROWW_GREEN} !important; font-weight: 600 !important; text-align: center !important;
    }}
    .element-container:has(.gw-mark-active) + .element-container button {{
        background: #d8ece2 !important;
    }}
    .element-container:has(.gw-mark-active) + .element-container button p {{
        color: #0f172a !important; font-weight: 600 !important;
    }}

    .gw-facts-card {{
        background: #e4f1eb; border-radius: 10px; padding: 0.85rem 0.9rem;
        margin: 1rem 0 0.6rem; color: #14532d;
    }}
    .gw-facts-card b {{ display: block; font-size: 0.85rem; margin-bottom: 0.35rem; }}
    .gw-facts-card p {{ font-size: 0.76rem; line-height: 1.45; margin: 0 0 0.5rem; color: #3f6b57; }}
    .gw-facts-card .gw-strong {{ font-size: 0.76rem; font-weight: 700; color: #14532d; }}

    .gw-user {{
        display: flex; align-items: center; gap: 0.6rem;
        border: 1px solid #dbe7e1; background: #ffffff;
        border-radius: 999px; padding: 0.4rem 0.75rem; margin-top: 0.6rem;
    }}
    .gw-avatar {{
        width: 30px; height: 30px; border-radius: 50%; background: {GROWW_GREEN};
        color: #fff; font-size: 0.7rem; font-weight: 700; flex: none;
        display: flex; align-items: center; justify-content: center;
    }}
    .gw-user-name {{ font-size: 0.85rem; font-weight: 600; color: #111827; }}

    /* ---------- Main header ---------- */
    .gw-header {{ display: flex; align-items: flex-start; gap: 0.9rem; }}
    .gw-bot {{
        width: 44px; height: 44px; border-radius: 50%; flex: none;
        background: #e4f1eb; display: flex; align-items: center;
        justify-content: center; font-size: 1.3rem;
    }}
    .gw-title {{ font-size: 1.6rem; font-weight: 700; color: #111827; margin: 0; }}
    .gw-subtitle {{ font-size: 0.86rem; color: #6b7280; margin: 0.15rem 0 0.6rem; }}
    .gw-pills {{ display: flex; flex-wrap: wrap; gap: 0.45rem; }}
    .gw-pill {{
        background: #f3f6f5; border: 1px solid #e2e8f0; border-radius: 999px;
        padding: 0.22rem 0.65rem; font-size: 0.74rem; color: #475569; font-weight: 500;
    }}

    /* ---------- Ask bar ---------- */
    div[data-testid="stForm"] {{
        border: 1px solid #d8e3de; border-radius: 14px;
        padding: 0.3rem 0.45rem 0.3rem 0.9rem; background: #fff;
        box-shadow: 0 1px 2px rgba(16,24,40,0.04); margin-top: 1.1rem;
    }}
    div[data-testid="stForm"] input {{
        border: none !important; box-shadow: none !important;
        font-size: 0.92rem; padding-left: 0; background: transparent;
    }}
    div[data-testid="stForm"] input::placeholder {{ color: #9ca3af; }}
    div[data-testid="stForm"] .stButton > button {{
        background: {GROWW_GREEN}; border: none; border-radius: 10px;
        padding: 0.4rem 0.8rem; min-height: 0; width: 100%;
    }}
    div[data-testid="stForm"] .stButton > button p {{
        color: #fff; font-weight: 600; font-size: 0.85rem; margin: 0;
    }}
    div[data-testid="stForm"] .stButton > button:hover {{ background: #009e77; }}

    /* ---------- Grouped button rows ---------- */
    .gw-group-label {{
        font-size: 0.8rem; font-weight: 600; color: #374151; margin: 1.15rem 0 0.45rem;
    }}
    .element-container:has(.gw-mark-chips) + div[data-testid="stHorizontalBlock"] button {{
        background: #fff; border: 1px solid #dfe6e3; border-radius: 999px;
        padding: 0.3rem 0.4rem; min-height: 0; width: 100%;
    }}
    .element-container:has(.gw-mark-chips) + div[data-testid="stHorizontalBlock"] button p {{
        font-size: 0.78rem; font-weight: 500; color: #374151; margin: 0; white-space: nowrap;
    }}
    .element-container:has(.gw-mark-follow) + div[data-testid="stHorizontalBlock"] button {{
        background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
        padding: 0.6rem 0.7rem; min-height: 3.4rem; width: 100%;
        justify-content: flex-start; align-items: flex-start;
    }}
    .element-container:has(.gw-mark-follow) + div[data-testid="stHorizontalBlock"] button p {{
        font-size: 0.78rem; color: #374151; text-align: left; line-height: 1.35; margin: 0;
    }}
    .element-container:has(.gw-mark-feedback) + div[data-testid="stHorizontalBlock"] button {{
        background: #fff; border: 1px solid #e2e8f0; border-radius: 9px;
        padding: 0.32rem 0.4rem; min-height: 0; width: 100%;
    }}
    .element-container:has(.gw-mark-feedback) + div[data-testid="stHorizontalBlock"] button p {{
        font-size: 0.76rem; color: #374151; margin: 0; white-space: nowrap;
    }}
    .element-container:has(.gw-mark-chips) + div[data-testid="stHorizontalBlock"] button:hover,
    .element-container:has(.gw-mark-follow) + div[data-testid="stHorizontalBlock"] button:hover,
    .element-container:has(.gw-mark-feedback) + div[data-testid="stHorizontalBlock"] button:hover {{
        border-color: {GROWW_GREEN};
    }}

    /* ---------- Conversation ---------- */
    .gw-user-row {{ display: flex; justify-content: flex-end; gap: 0.6rem; margin: 1.5rem 0 0.2rem; }}
    .gw-bubble {{
        background: #d8f0e4; color: #14532d; border-radius: 14px 14px 2px 14px;
        padding: 0.75rem 0.95rem; font-size: 0.9rem; line-height: 1.5; max-width: 68%;
    }}
    .gw-bubble .gw-time {{
        display: block; text-align: right; font-size: 0.68rem;
        color: #4f8a70; margin-top: 0.35rem;
    }}
    .gw-answer-row {{ display: flex; gap: 0.6rem; margin-top: 1rem; }}
    .gw-card {{
        border: 1px solid #e5eae8; border-radius: 14px; background: #fff;
        padding: 1.1rem 1.2rem; flex: 1; color: #1f2937;
        font-size: 0.9rem; line-height: 1.6;
    }}
    .gw-card > div {{ margin-bottom: 0.15rem; }}
    .gw-card .gw-qhead {{
        font-weight: 700; color: #111827; margin: 0.95rem 0 0.3rem; font-size: 0.93rem;
    }}
    .gw-card > .gw-qhead:first-child {{ margin-top: 0; }}
    .gw-card .gw-src {{ font-size: 0.8rem; color: #6b7280; margin-top: 0.4rem; }}
    .gw-card a {{ color: #2563eb; text-decoration: none; word-break: break-word; }}
    .gw-note {{
        border-top: 1px solid #eef2f0; margin-top: 0.9rem; padding-top: 0.65rem;
        font-size: 0.76rem; color: #6b7280;
    }}

    /* ---------- Sources ---------- */
    .gw-sources {{
        border: 1px solid #e5eae8; border-radius: 14px; background: #fff;
        margin: 0.75rem 0 0.2rem 3.05rem; overflow: hidden;
    }}
    .gw-sources-head {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 0.7rem 1rem; border-bottom: 1px solid #eef2f0;
        font-size: 0.85rem; font-weight: 700; color: #111827;
    }}
    .gw-sources-head span {{ font-size: 0.76rem; font-weight: 600; color: {GROWW_GREEN}; }}
    .gw-source {{
        display: flex; align-items: center; gap: 0.7rem;
        padding: 0.6rem 1rem; border-bottom: 1px solid #f4f7f6;
    }}
    .gw-source:last-child {{ border-bottom: none; }}
    .gw-source-icon {{
        width: 26px; height: 26px; border-radius: 6px; flex: none;
        background: #eaf5f0; display: flex; align-items: center; justify-content: center;
    }}
    .gw-source-text {{ flex: 1; min-width: 0; }}
    .gw-source-title {{ font-size: 0.82rem; font-weight: 600; color: #111827; }}
    .gw-source-sub {{ font-size: 0.74rem; color: #6b7280; }}
    .gw-source-view {{
        font-size: 0.76rem; font-weight: 600; color: #374151; text-decoration: none;
        border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.25rem 0.6rem;
    }}

    /* ---------- Footer / empty state ---------- */
    .gw-feedback-label {{ font-size: 0.8rem; color: #374151; padding-top: 0.4rem; }}
    .gw-foot {{
        text-align: center; font-size: 0.74rem; color: #9ca3af;
        border-top: 1px solid #eef2f0; margin-top: 2.2rem; padding-top: 0.9rem;
    }}
    .gw-empty {{
        border: 1px dashed #dfe8e4; border-radius: 14px; padding: 2rem 1.5rem;
        text-align: center; color: #6b7280; font-size: 0.88rem;
        line-height: 1.6; margin-top: 1.4rem;
    }}
</style>
"""
