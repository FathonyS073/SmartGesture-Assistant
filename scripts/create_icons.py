"""Create original minimalist vector icon assets (no institutional trademark)."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'assets'/'icons'
ROOT.mkdir(parents=True,exist_ok=True)
# All path geometry built with SVG stroke, no external icon package.
paths={
'landmark':'<path d="M3 10 24 2l21 8"/><path d="M6 13h36M4 43h40M9 38V16m10 22V16m10 22V16m10 22V16"/>',
'building':'<rect x="5" y="14" width="17" height="30" rx="2"/><rect x="26" y="5" width="17" height="39" rx="2"/><path d="M12 20h3m-3 7h3m-3 7h3m18-20h3m-3 8h3m-3 8h3M21 44h7"/>',
'graduation':'<path d="m3 17 21-10 21 10-21 10L3 17Zm8 7v10q13 11 26 0V24M45 17v15"/>',
'monitor':'<rect x="4" y="7" width="40" height="29" rx="4"/><path d="M24 36v7M14 43h20M19 16l-6 6 6 6m10-12 6 6-6 6m-3-14-4 17"/>',
'file':'<path d="M9 4h24l7 7v30a3 3 0 0 1-3 3H9a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3Z"/><path d="M31 4v10h9M13 22h20M13 30h13M13 37h15"/>',
'users':'<circle cx="18" cy="15" r="7"/><circle cx="34" cy="18" r="5"/><path d="M4 42v-5c0-9 28-9 28 0v5H4Zm30-20c9 0 11 9 11 13v7H36"/>',
'award':'<circle cx="24" cy="17" r="12"/><path d="m15 28-4 17 13-6 13 6-4-17M19 17l3 3 7-8"/>',
'people':'<circle cx="16" cy="15" r="6"/><circle cx="32" cy="15" r="6"/><path d="M2 43v-6c0-12 22-12 22 0v6Zm23 0v-6c0-12 21-12 21 0v6Z"/>',
'microscope':'<path d="M22 5 34 15l-5 6-12-10 5-6Zm-8 11 10 9M19 25l-7 9M8 43h34M16 39h18M31 24c10 3 11 14 1 15"/>',
'map-pin':'<path d="M24 45S8 28 8 18a16 16 0 1 1 32 0c0 10-16 27-16 27Z"/><circle cx="24" cy="18" r="6"/>',
'camera':'<path d="M5 12h9l4-5h12l4 5h9v29H5V12Z"/><circle cx="24" cy="26" r="9"/>',
'hand':'<path d="M15 42 6 29q-2-5 3-7l6 6V11q0-6 5-5t3 6V6q0-5 5-4t3 6V6q0-5 5-3t2 7v1q3-4 6 0v18c0 9-7 14-15 14H15Z"/>',
'check':'<path d="M8 25 19 36 41 12"/>',
'back':'<path d="M34 10 19 24l15 14M20 24h24"/>',
'settings':'<circle cx="24" cy="24" r="8"/><path d="M20 3h8l2 6 6 3 6-2 4 7-5 5v5l5 4-4 7-7-1-5 3-2 6h-8l-2-6-6-3-7 1-4-7 5-4v-5l-5-5 4-7 6 2 6-3z"/>',
'help':'<circle cx="24" cy="24" r="20"/><path d="M17 17a8 8 0 0 1 15 3c0 5-8 6-8 11M24 38v1"/>',
'volume':'<path d="M6 18h10l10-10v32L16 30H6V18ZM32 16q10 8 0 16M37 10q16 14 0 28"/>',
'profile':'<circle cx="24" cy="15" r="8"/><path d="M7 44v-5c0-17 34-17 34 0v5"/>',
}
colors={'award':'#7153df','users':'#ec5149','map-pin':'#e94242','people':'#05895d','building':'#048657', 'check':'#08783f','back':'#e02436'}
for name,body in paths.items():
    color=colors.get(name,'#126bc0')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"><g fill="none" stroke="{color}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>'
    (ROOT/(name+'.svg')).write_text(svg,encoding='utf-8')
print(len(paths),'SVG icons')
