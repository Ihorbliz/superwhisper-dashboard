#!/usr/bin/env python3
"""
SuperWhisper Dashboard Generator
=================================
Reads history.json, computes per-period stats, generates dashboard HTML.

Usage:
    python generate_dashboard.py --lang ua    # Ukrainian
    python generate_dashboard.py --lang en    # English
    python generate_dashboard.py --lang both  # both (default)
"""

import json, os, sys, webbrowser, argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import config

HISTORY_FILE = Path(__file__).parent / "history.json"
TYPING_WPM   = getattr(config, 'TYPING_WPM', 44)

STRINGS = {
    'ua': {
        'lang':          'uk',
        'title':         'SuperWhisper — мій голос',
        'subtitle':      'статистика голосових записів',
        'updated':       'оновлено',
        'tabs':          [('day','День'),('week','Тиждень'),('month','Місяць'),('year','Рік'),('all','Весь час')],
        'card_saved':    'Зекономлено часу',
        'saved_sub':     'замість набору на клавіатурі',
        'saved_badge':   f'vs {TYPING_WPM} WPM набору',
        'card_words':    'Слів наговорено',
        'words_badge':   'WPM мовлення',
        'card_meetings': 'Зустрічі',
        'meet_sub':      'год записано',
        'meet_badge':    'не в економії',
        'card_dict':     'Диктовка',
        'dict_badge':    'разом надиктовано',
        'unit_h':        'год',
        'unit_m':        'хв',
        'dictations':    'диктовок',
        'recordings':    'записів',
        'speed_wpm':     'WPM мовлення',
        'ch1_title':     'Активність за 60 днів',
        'ch1_desc':      'хвилини диктовки та зустрічей по днях',
        'all_title':     'Загальна статистика',
        'all_desc':      'всі записи за весь час',
        'mini_dh':       'год диктовки',
        'mini_mh':       'год зустрічей',
        'mini_tot':      'всього записів',
        'mini_spd':      'WPM швидкість',
        'ch2_title':     'Зекономлений час по днях',
        'ch2_desc':      'хвилини, які ти не витратив на набір',
        'ch3_title':     'Активність по годинах',
        'ch3_desc':      'коли ти найбільше диктуєш',
        'ds_dict':       'Диктовка (хв)',
        'ds_meet':       'Зустрічі (хв)',
        'ds_saved':      'Зекономлено (хв)',
        'ds_hourly':     'Хвилини',
        'tip_h':         'год зекономлено',
        'tip_m':         'хв зекономлено',
        'locale':        'uk-UA',
    },
    'en': {
        'lang':          'en',
        'title':         'SuperWhisper — my voice',
        'subtitle':      'voice recording statistics',
        'updated':       'updated',
        'tabs':          [('day','Day'),('week','Week'),('month','Month'),('year','Year'),('all','All time')],
        'card_saved':    'Time saved',
        'saved_sub':     'instead of typing',
        'saved_badge':   f'vs {TYPING_WPM} WPM typing',
        'card_words':    'Words dictated',
        'words_badge':   'WPM speaking',
        'card_meetings': 'Meetings',
        'meet_sub':      'hrs recorded',
        'meet_badge':    'excluded from savings',
        'card_dict':     'Dictation',
        'dict_badge':    'total dictated',
        'unit_h':        'h',
        'unit_m':        'min',
        'dictations':    'dictations',
        'recordings':    'recordings',
        'speed_wpm':     'WPM speaking',
        'ch1_title':     'Activity over 60 days',
        'ch1_desc':      'dictation and meeting minutes per day',
        'all_title':     'Overall statistics',
        'all_desc':      'all recordings, all time',
        'mini_dh':       'hrs dictation',
        'mini_mh':       'hrs meetings',
        'mini_tot':      'total recordings',
        'mini_spd':      'WPM speed',
        'ch2_title':     'Time saved per day',
        'ch2_desc':      'minutes you did not spend typing',
        'ch3_title':     'Activity by hour',
        'ch3_desc':      'when you dictate the most',
        'ds_dict':       'Dictation (min)',
        'ds_meet':       'Meetings (min)',
        'ds_saved':      'Saved (min)',
        'ds_hourly':     'Minutes',
        'tip_h':         'h saved',
        'tip_m':         'min saved',
        'locale':        'en-US',
    },
}


def load_history():
    if not HISTORY_FILE.exists():
        print("history.json not found. Run sync_history.py first.")
        return None
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_period_stats(recordings, days=None):
    if days is not None:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        recordings = [r for r in recordings if r.get('datetime', '') >= cutoff]
    dictation = [r for r in recordings if r.get('recording_type') == 'dictation']
    meetings  = [r for r in recordings if r.get('recording_type') == 'meeting']
    total_words    = sum(r.get('word_count', 0) for r in dictation)
    total_dict_min = sum(r.get('duration_minutes', 0) for r in dictation)
    total_meet_min = sum(r.get('duration_minutes', 0) for r in meetings)
    typing_min     = total_words / TYPING_WPM if TYPING_WPM else 0
    saved_min      = max(0, typing_min - total_dict_min)
    avg_speed      = (total_words / total_dict_min) if total_dict_min > 0 else 0
    return {
        'saved_min':        round(saved_min, 1),
        'total_words':      total_words,
        'total_dictations': len(dictation),
        'total_meetings':   len(meetings),
        'total_dict_hours': round(total_dict_min / 60, 1),
        'total_meet_hours': round(total_meet_min / 60, 1),
        'avg_speed_wpm':    round(avg_speed, 1),
    }


def compute_chart_data(recordings, days=60):
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    daily  = defaultdict(lambda: {'dict_min': 0.0, 'words': 0, 'meet_min': 0.0})
    for r in recordings:
        dt = r.get('datetime', '')
        if dt < cutoff:
            continue
        day = dt[:10]
        if r.get('recording_type') == 'dictation':
            daily[day]['dict_min'] += r.get('duration_minutes', 0)
            daily[day]['words']    += r.get('word_count', 0)
        else:
            daily[day]['meet_min'] += r.get('duration_minutes', 0)
    sd = sorted(daily.keys())
    return {
        'labels':    sd,
        'dict_min':  [round(daily[d]['dict_min'], 1) for d in sd],
        'meet_min':  [round(daily[d]['meet_min'], 1) for d in sd],
        'saved_min': [round(max(0, daily[d]['words'] / TYPING_WPM - daily[d]['dict_min']), 1) for d in sd],
    }


def compute_hourly(recordings):
    hd = defaultdict(float)
    for r in recordings:
        if r.get('recording_type') == 'dictation':
            try:
                hd[int(r['datetime'][11:13])] += r.get('duration_minutes', 0)
            except Exception:
                pass
    return [round(hd.get(h, 0), 1) for h in range(24)]


def generate_html(all_recs, last_sync, lang='ua'):
    s = STRINGS[lang]
    jd = lambda v: json.dumps(v, ensure_ascii=False)

    day_s   = compute_period_stats(all_recs, days=1)
    week_s  = compute_period_stats(all_recs, days=7)
    month_s = compute_period_stats(all_recs, days=30)
    year_s  = compute_period_stats(all_recs, days=365)
    all_s   = compute_period_stats(all_recs)
    chart   = compute_chart_data(all_recs)
    hourly  = compute_hourly(all_recs)
    sync_str = last_sync[:16].replace('T', ' ') if last_sync else '-'

    period_data = {'day': day_s, 'week': week_s, 'month': month_s, 'year': year_s, 'all': all_s}

    tabs_html = ''.join(
        '<button class="tab' + (' active' if i == 1 else '') + '" data-period="' + p + '">' + label + '</button>'
        for i, (p, label) in enumerate(s['tabs'])
    )

    hlabels = ['{:02d}:00'.format(h) for h in range(24)]

    p = []
    p.append('<!DOCTYPE html>\n<html lang="' + s['lang'] + '">\n<head>\n')
    p.append('<meta charset="UTF-8">\n')
    p.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
    p.append('<title>' + s['title'] + '</title>\n')
    p.append('<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.js" ')
    p.append('integrity="sha384-iU8HYtnGQ8Cy4zl7gbNMOhsDTTKX02BTXptVP/vqAWIaTfM7isw76iyZCsjL2eVi" ')
    p.append('crossorigin="anonymous"></script>\n')
    p.append('''<style>
:root {
  --bg:#f2f2f7; --surface:#fff; --border:#e5e5ea; --text:#1c1c1e;
  --muted:#8e8e93; --accent:#007aff; --green:#30d158; --orange:#ff9f0a;
  --r:18px; --rs:12px; color-scheme:light;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display','Segoe UI',system-ui,sans-serif;
  background:var(--bg);color:var(--text);min-height:100vh;padding:32px 28px 56px;
  -webkit-font-smoothing:antialiased}
.header{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:28px}
.header h1{font-size:26px;font-weight:700;letter-spacing:-.5px}
.header p{font-size:13px;color:var(--muted);margin-top:3px}
.sync-badge{font-size:12px;color:var(--muted);background:var(--surface);
  border:1px solid var(--border);padding:6px 12px;border-radius:20px;white-space:nowrap}
.tabs{display:flex;flex-wrap:nowrap;width:100%;background:var(--surface);
  border:1px solid var(--border);border-radius:12px;padding:4px;margin-bottom:24px;gap:2px}
.tab{flex:1;font-size:13px;font-weight:500;padding:7px 6px;border-radius:9px;cursor:pointer;
  border:none;background:transparent;color:var(--muted);
  transition:background 180ms ease,color 180ms ease;white-space:nowrap;text-align:center}
.tab.active{background:var(--accent);color:#fff}
.tab:not(.active):hover{background:var(--bg);color:var(--text)}
.grid{display:grid;gap:16px}
.g4{grid-template-columns:repeat(4,1fr)}
.g2{grid-template-columns:2fr 1fr}
.g2e{grid-template-columns:1fr 1fr}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:22px 24px}
.card-label{font-size:11px;font-weight:600;color:var(--muted);letter-spacing:.5px;
  text-transform:uppercase;margin-bottom:10px}
.card-value{font-size:42px;font-weight:700;letter-spacing:-2px;line-height:1;
  transition:opacity 200ms ease,transform 200ms cubic-bezier(.22,1,.36,1)}
.card-value.updating{opacity:0;transform:translateY(6px)}
.card-unit{font-size:20px;font-weight:500;letter-spacing:-.5px}
.card-sub{font-size:13px;color:var(--muted);margin-top:8px}
.badge{display:inline-block;font-size:11px;font-weight:600;
  padding:3px 8px;border-radius:20px;margin-top:10px}
.b-green{background:#d1fae5;color:#065f46}
.b-blue{background:#dbeafe;color:#1e40af}
.b-orange{background:#fff3cd;color:#92400e}
.stat-card{opacity:0;transform:translateY(18px);
  transition:opacity 400ms cubic-bezier(.22,1,.36,1),transform 400ms cubic-bezier(.22,1,.36,1)}
.stat-card.visible{opacity:1;transform:translateY(0)}
.stat-card:nth-child(1){transition-delay:0ms}
.stat-card:nth-child(2){transition-delay:60ms}
.stat-card:nth-child(3){transition-delay:120ms}
.stat-card:nth-child(4){transition-delay:180ms}
.chart-card{opacity:0;transform:translateY(18px);
  transition:opacity 400ms cubic-bezier(.22,1,.36,1) 220ms,transform 400ms cubic-bezier(.22,1,.36,1) 220ms}
.chart-card.visible{opacity:1;transform:translateY(0)}
.card-title{font-size:15px;font-weight:600;margin-bottom:2px}
.card-desc{font-size:12px;color:var(--muted)}
.chart-wrap{position:relative;height:200px;margin-top:16px}
.chart-wrap-sm{position:relative;height:150px;margin-top:16px}
.mini-stats{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px}
.mini-stat{background:var(--bg);border-radius:var(--rs);padding:14px 16px}
.mini-val{font-size:22px;font-weight:700;letter-spacing:-.5px}
.mini-lbl{font-size:11px;color:var(--muted);margin-top:3px}
@media(max-width:920px){.g4{grid-template-columns:1fr 1fr}.g2{grid-template-columns:1fr}.g2e{grid-template-columns:1fr}}
@media(max-width:600px){
  body{padding:16px 14px 48px}
  .header{flex-direction:column;gap:10px;align-items:flex-start}
  .sync-badge{align-self:flex-start}
  .g4{grid-template-columns:1fr 1fr;gap:12px}
  .g2,.g2e{grid-template-columns:1fr}
  .card{padding:16px 18px}
  .card-value{font-size:34px;letter-spacing:-1.5px}
  .card-unit{font-size:17px}
  .chart-wrap{height:160px}
  .chart-wrap-sm{height:130px}
  .grid{gap:12px}
}
</style></head><body>\n''')

    p.append('<div class="header"><div>')
    p.append('<h1>SuperWhisper</h1>')
    p.append('<p>' + s['subtitle'] + '</p></div>')
    p.append('<div class="sync-badge">' + s['updated'] + ' ' + sync_str + '</div></div>\n')
    p.append('<div class="tabs" id="tabs">' + tabs_html + '</div>\n')

    p.append('<div class="grid g4" id="cards" style="margin-bottom:16px">\n')
    p.append('  <div class="card stat-card"><div class="card-label">' + s['card_saved'] + '</div>')
    p.append('<div class="card-value" id="v-saved" style="color:var(--green)">-</div>')
    p.append('<div class="card-sub" id="sub-saved">' + s['saved_sub'] + '</div>')
    p.append('<span class="badge b-green">' + s['saved_badge'] + '</span></div>\n')

    p.append('  <div class="card stat-card"><div class="card-label">' + s['card_words'] + '</div>')
    p.append('<div class="card-value" id="v-words">-</div>')
    p.append('<div class="card-sub" id="sub-words">' + s['dictations'] + '</div>')
    p.append('<span class="badge b-blue" id="badge-speed">- ' + s['words_badge'] + '</span></div>\n')

    p.append('  <div class="card stat-card"><div class="card-label">' + s['card_meetings'] + '</div>')
    p.append('<div class="card-value" id="v-meetings">-</div>')
    p.append('<div class="card-sub" id="sub-meetings">- ' + s['meet_sub'] + '</div>')
    p.append('<span class="badge b-orange">' + s['meet_badge'] + '</span></div>\n')

    p.append('  <div class="card stat-card"><div class="card-label">' + s['card_dict'] + '</div>')
    p.append('<div class="card-value" id="v-dicthours" style="color:var(--accent)">-<span class="card-unit">' + s['unit_h'] + '</span></div>')
    p.append('<div class="card-sub" id="sub-dicthours">- ' + s['recordings'] + '</div>')
    p.append('<span class="badge b-blue">' + s['dict_badge'] + '</span></div>\n')
    p.append('</div>\n')

    p.append('<div class="grid g2 chart-card" id="charts1" style="margin-bottom:16px">\n')
    p.append('  <div class="card"><div class="card-title">' + s['ch1_title'] + '</div>')
    p.append('<div class="card-desc">' + s['ch1_desc'] + '</div>')
    p.append('<div class="chart-wrap"><canvas id="dailyChart"></canvas></div></div>\n')
    p.append('  <div class="card"><div class="card-title">' + s['all_title'] + '</div>')
    p.append('<div class="card-desc">' + s['all_desc'] + '</div>')
    p.append('<div class="mini-stats">')
    p.append('<div class="mini-stat"><div class="mini-val">' + str(all_s['total_dict_hours']) + '</div><div class="mini-lbl">' + s['mini_dh'] + '</div></div>')
    p.append('<div class="mini-stat"><div class="mini-val">' + str(all_s['total_meet_hours']) + '</div><div class="mini-lbl">' + s['mini_mh'] + '</div></div>')
    p.append('<div class="mini-stat"><div class="mini-val">' + str(all_s['total_dictations'] + all_s['total_meetings']) + '</div><div class="mini-lbl">' + s['mini_tot'] + '</div></div>')
    p.append('<div class="mini-stat"><div class="mini-val">' + str(all_s['avg_speed_wpm']) + '</div><div class="mini-lbl">' + s['mini_spd'] + '</div></div>')
    p.append('</div></div>\n</div>\n')

    p.append('<div class="grid g2e chart-card" id="charts2">\n')
    p.append('  <div class="card"><div class="card-title">' + s['ch2_title'] + '</div>')
    p.append('<div class="card-desc">' + s['ch2_desc'] + '</div>')
    p.append('<div class="chart-wrap-sm"><canvas id="savedChart"></canvas></div></div>\n')
    p.append('  <div class="card"><div class="card-title">' + s['ch3_title'] + '</div>')
    p.append('<div class="card-desc">' + s['ch3_desc'] + '</div>')
    p.append('<div class="chart-wrap-sm"><canvas id="hourlyChart"></canvas></div></div>\n')
    p.append('</div>\n')

    p.append('<script>\n')
    p.append('const DATA=' + jd(period_data) + ';\n')
    p.append('const chartLabels=' + jd(chart['labels']) + ';\n')
    p.append('const chartDict=' + jd(chart['dict_min']) + ';\n')
    p.append('const chartMeet=' + jd(chart['meet_min']) + ';\n')
    p.append('const chartSaved=' + jd(chart['saved_min']) + ';\n')
    p.append('const hourlyData=' + jd(hourly) + ';\n')
    p.append('const hLabels=' + jd(hlabels) + ';\n')
    p.append('const TIP_H=' + jd(s['tip_h']) + ';\n')
    p.append('const TIP_M=' + jd(s['tip_m']) + ';\n')
    p.append('const UNIT_H=' + jd(s['unit_h']) + ';\n')
    p.append('const UNIT_M=' + jd(s['unit_m']) + ';\n')
    p.append('const LOCALE=' + jd(s['locale']) + ';\n')
    p.append('const STR_DICT=' + jd(s['dictations']) + ';\n')
    p.append('const STR_REC=' + jd(s['recordings']) + ';\n')
    p.append('const STR_MEET_SUB=' + jd(s['meet_sub']) + ';\n')
    p.append('const STR_SPEED=' + jd(s['speed_wpm']) + ';\n')
    p.append('const DS_DICT=' + jd(s['ds_dict']) + ';\n')
    p.append('const DS_MEET=' + jd(s['ds_meet']) + ';\n')
    p.append('const DS_SAVED=' + jd(s['ds_saved']) + ';\n')
    p.append('const DS_HOURLY=' + jd(s['ds_hourly']) + ';\n')

    p.append('''
Chart.defaults.font.family="-apple-system,BlinkMacSystemFont,'SF Pro Display','Segoe UI',sans-serif";
Chart.defaults.font.size=11;
Chart.defaults.color='#8e8e93';

new Chart(document.getElementById('dailyChart'),{
  type:'bar',
  data:{labels:chartLabels,datasets:[
    {label:DS_DICT,data:chartDict,backgroundColor:'rgba(0,122,255,0.18)',borderColor:'rgba(0,122,255,0.7)',borderWidth:1.5,borderRadius:4},
    {label:DS_MEET,data:chartMeet,backgroundColor:'rgba(255,159,10,0.15)',borderColor:'rgba(255,159,10,0.6)',borderWidth:1.5,borderRadius:4}
  ]},
  options:{responsive:true,maintainAspectRatio:false,
    animation:{duration:800,easing:'easeOutQuart'},
    plugins:{legend:{position:'top',labels:{boxWidth:10,padding:12}}},
    scales:{x:{grid:{display:false},ticks:{maxTicksLimit:12,maxRotation:0}},y:{grid:{color:'rgba(0,0,0,0.04)'},ticks:{maxTicksLimit:5}}}}
});

new Chart(document.getElementById('savedChart'),{
  type:'line',
  data:{labels:chartLabels,datasets:[{
    label:DS_SAVED,data:chartSaved,
    borderColor:'#30d158',backgroundColor:'rgba(48,209,88,0.08)',
    borderWidth:2,pointRadius:0,pointHoverRadius:5,
    pointHoverBackgroundColor:'#30d158',pointHoverBorderColor:'#fff',pointHoverBorderWidth:2,
    tension:0.4,fill:true
  }]},
  options:{responsive:true,maintainAspectRatio:false,
    animation:{duration:900,easing:'easeOutQuart'},
    interaction:{mode:'index',intersect:false},
    plugins:{legend:{display:false},tooltip:{
      backgroundColor:'#1c1c1e',titleColor:'#8e8e93',bodyColor:'#fff',
      padding:12,cornerRadius:10,
      titleFont:{size:11},bodyFont:{size:14,weight:'700'},
      callbacks:{
        title:ctx=>ctx[0].label,
        label:ctx=>{const v=ctx.parsed.y;return ' '+(v>=60?(v/60).toFixed(1)+' '+TIP_H:Math.round(v)+' '+TIP_M);}
      }
    }},
    scales:{x:{grid:{display:false},ticks:{maxTicksLimit:8,maxRotation:0}},y:{grid:{color:'rgba(0,0,0,0.04)'},ticks:{maxTicksLimit:4}}}}
});

new Chart(document.getElementById('hourlyChart'),{
  type:'bar',
  data:{labels:hLabels,datasets:[{label:DS_HOURLY,data:hourlyData,backgroundColor:'rgba(0,122,255,0.15)',borderColor:'rgba(0,122,255,0.5)',borderWidth:1,borderRadius:3}]},
  options:{responsive:true,maintainAspectRatio:false,animation:{duration:700,easing:'easeOutQuart'},
    plugins:{legend:{display:false}},
    scales:{x:{grid:{display:false},ticks:{maxTicksLimit:8,maxRotation:0}},y:{grid:{color:'rgba(0,0,0,0.04)'},ticks:{maxTicksLimit:4}}}}
});

function fmtSaved(s){return s.saved_min>=60?(s.saved_min/60).toFixed(1):Math.round(s.saved_min).toString();}
function savedUnit(s){return s.saved_min>=60?'<span class="card-unit">'+UNIT_H+'</span>':'<span class="card-unit">'+UNIT_M+'</span>';}
function fmtNum(n){return n.toLocaleString(LOCALE);}

function updateCards(period){
  const d=DATA[period];
  [{id:'v-saved',html:fmtSaved(d)+savedUnit(d)},
   {id:'v-words',html:fmtNum(d.total_words)},
   {id:'v-meetings',html:String(d.total_meetings)},
   {id:'v-dicthours',html:d.total_dict_hours+'<span class="card-unit">'+UNIT_H+'</span>'}
  ].forEach(v=>{
    const el=document.getElementById(v.id);
    el.classList.add('updating');
    setTimeout(()=>{el.innerHTML=v.html;el.classList.remove('updating');},200);
  });
  document.getElementById('sub-words').textContent=d.total_dictations+' '+STR_DICT;
  document.getElementById('sub-meetings').textContent=d.total_meet_hours+' '+STR_MEET_SUB;
  document.getElementById('sub-dicthours').textContent=d.total_dictations+' '+STR_REC;
  document.getElementById('badge-speed').textContent=d.avg_speed_wpm+' '+STR_SPEED;
}

document.getElementById('tabs').addEventListener('click',e=>{
  const btn=e.target.closest('.tab');if(!btn)return;
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  btn.classList.add('active');
  updateCards(btn.dataset.period);
});

const obs=new IntersectionObserver(entries=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      const cards=e.target.querySelectorAll('.stat-card,.chart-card');
      cards.length?cards.forEach(c=>c.classList.add('visible')):e.target.classList.add('visible');
    }
  });
},{threshold:0.1});
document.querySelectorAll('.stat-card,.chart-card,#cards,#charts1,#charts2').forEach(el=>obs.observe(el));
document.querySelector('[data-period="week"]').click();
</script></body></html>''')

    return ''.join(p)


def main():
    parser = argparse.ArgumentParser(description='Generate SuperWhisper dashboard')
    parser.add_argument('--lang', choices=['ua', 'en', 'both'], default='both')
    args = parser.parse_args()

    history = load_history()
    if not history:
        return
    recordings = history.get('recordings', [])
    if not recordings:
        print("No recordings found. Run sync_history.py first.")
        return

    base  = Path(__file__).parent
    langs = ['ua', 'en'] if args.lang == 'both' else [args.lang]

    for lang in langs:
        out  = base / ('dashboard_' + lang + '.html')
        html = generate_html(recordings, history.get('last_sync'), lang=lang)
        with open(out, 'w', encoding='utf-8') as f:
            f.write(html)
        print('Generated: ' + str(out))

    open_lang = 'ua' if args.lang in ('ua', 'both') else 'en'
    open_file = base / ('dashboard_' + open_lang + '.html')
    try:
        if sys.platform == 'win32':
            os.startfile(str(open_file))
        else:
            webbrowser.open(open_file.as_uri())
    except Exception:
        webbrowser.open(open_file.as_uri())


if __name__ == '__main__':
    main()
