"""제19회차 LOLEX 임시점수표 기준, 이원빈(탑/미드 45) + 김민규(원딜 59.5) 포함
팀 합계가 정확히 TARGET점인 모든 조합을 엑셀로 출력한다."""
from itertools import product
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

TARGET = 228.0
OUT = "LOLEX_19회차_팀조합_228점.xlsx"

# (이름, 점수, 빨간점수(!) 여부, #부라인 표시 여부)
R, S = True, True
TABLE = {
    "탑": [
        ("김지원", 55, 0, 0), ("정제우", 50, 0, 0), ("김두엽", 50, 0, 0), ("강희민", 49, 0, 0),
        ("원성현", 49, R, 0), ("강용현", 48, 0, 0), ("반재성", 48, 0, 0), ("유동하", 47.5, 0, 0),
        ("오세진", 47, 0, 0), ("정성윤", 47, 0, 0), ("김승환", 46, 0, S), ("남지수", 45, 0, 0),
        ("이원빈", 45, 0, 0), ("이영훈", 44.5, R, 0), ("심진솔", 43.5, 0, 0), ("홍건표", 43, R, 0),
        ("김진모", 42, 0, 0), ("유재현", 42, 0, 0), ("공민석", 42, 0, 0), ("강규백", 42, 0, 0),
        ("한유찬", 41, 0, 0), ("김태환", 40, 0, 0), ("윤종현", 39, R, 0), ("고락우", 38.5, R, 0),
        ("정민혁", 38, R, 0), ("유영조", 36.5, 0, 0), ("김중원", 35.5, 0, 0),
    ],
    "정글": [
        ("정승욱", 59, R, 0), ("김주영", 58.5, 0, 0), ("송은수", 58, R, 0), ("지영환", 57.5, 0, 0),
        ("박주원", 57.5, R, 0), ("김한민", 56, R, 0), ("문현식", 55.5, 0, 0), ("김승환", 51, R, 0),
        ("박규태", 50, 0, 0), ("허세범", 49, 0, 0), ("김찬우", 48, 0, 0), ("조경신", 47.5, 0, 0),
        ("임천호", 45, R, 0), ("한창민", 43, R, 0), ("김경환", 43, R, S), ("고락우", 41, 0, 0),
        ("서필수", 39.5, R, 0), ("윤수근", 38.5, R, 0), ("김태환", 38.5, R, S), ("정태인", 31, 0, 0),
    ],
    "미드": [
        ("오근혁", 58, 0, 0), ("김기황", 57.5, 0, 0), ("김수현", 57, 0, 0), ("이태균", 57, R, 0),
        ("이호민", 53.5, R, 0), ("민태운", 53.5, 0, 0), ("김지후", 53, R, 0), ("김성민", 52, 0, 0),
        ("홍성진", 51.5, 0, 0), ("전찬혁", 50.5, 0, S), ("백승호", 49.5, 0, 0), ("윤민영", 47.5, R, 0),
        ("이규열", 46, R, 0), ("추재인", 46, 0, 0), ("노하람", 45.5, 0, 0), ("조시현", 45, 0, 0),
        ("김백호", 45, 0, 0), ("유수민", 44, 0, 0), ("이정현", 44, 0, 0), ("장하빈", 44, R, 0),
        ("원성민", 44, 0, 0), ("이정희", 43.5, R, 0), ("김보름", 43, R, 0), ("이륜금", 41, R, 0),
        ("이영현", 40, R, 0), ("최기쁨", 40, R, 0), ("이찬희", 39.5, R, 0), ("류한별", 37, R, 0),
        ("류연우", 35.5, 0, S), ("이윤서", 33, 0, 0),
    ],
    "원딜": [
        ("김서준", 62, 0, 0), ("김민규", 59.5, 0, 0), ("임경무", 57.5, 0, 0), ("윤대월", 57.5, R, 0),
        ("박주형", 57, 0, 0), ("이주아", 56.5, 0, 0), ("이광재", 56, 0, 0), ("이유빈", 54.5, 0, 0),
        ("안병헌", 54.5, 0, 0), ("김태강", 52, 0, 0), ("전찬혁", 51, 0, 0), ("김윤현", 50, 0, 0),
        ("최인규", 48, R, 0), ("성기동", 48, 0, 0), ("김진우", 46.5, 0, 0), ("양희성", 46.5, R, 0),
        ("이성현", 46, 0, 0), ("반재성", 44.5, 0, S), ("임진환", 44, 0, 0), ("조시현", 44, 0, S),
        ("강지호", 42.5, R, 0), ("김선건", 42.5, 0, 0), ("이정희", 42.5, 0, S), ("이도현", 41, R, 0),
        ("노하람", 40, 0, S), ("구본희", 36, 0, 0), ("권세희", 35, 0, 0), ("박현주", 32, 0, 0),
        ("김은유", 31, 0, 0),
    ],
    "서폿": [
        ("김경환", 42, 0, 0), ("윤대일", 41.5, R, 0), ("성기동", 41, R, 0), ("김민철", 40, R, 0),
        ("김찬우", 39.5, R, S), ("길기영", 39, 0, 0), ("이준범", 39, 0, 0), ("안병헌", 39, 0, S),
        ("김상학", 38, 0, 0), ("양희성", 36.5, 0, S), ("안은민", 36, 0, 0), ("이륜금", 36, 0, 0),
        ("이성현", 36, 0, S), ("장하빈", 36, 0, S), ("신단비", 35.5, 0, 0), ("공민석", 35, 0, 0),
        ("박승묵", 35, 0, 0), ("서필수", 34.5, R, 0), ("이영현", 34.5, 0, 0), ("최기쁨", 34, R, 0),
        ("송유진", 34, R, 0), ("설예준", 34, 0, 0), ("홍건표", 33.5, 0, 0), ("류한별", 33, 0, 0),
        ("류연우", 32.5, R, 0), ("정한나", 32, 0, 0), ("김지해", 31.5, 0, 0), ("김보름", 31.5, R, 0),
        ("이고은", 29, R, 0),
    ],
}
LANES = ["탑", "정글", "미드", "원딜", "서폿"]
FLEX_LANES = ["탑", "정글", "미드", "원딜"]  # 서폿 자리는 서폿 표에 있는 선수만


def build_options():
    """라인별 후보 목록: (이름, 점수, 구분) — 구분은 '표기' 또는 '이동(원라인)'.

    # 붙은 점수는 부라인(그 라인 전용), 서폿 점수는 서폿 전용.
    그 외(빨간 점수 포함)는 주라인 점수로 보고 본인 점수가 없는 다른 라인으로 이동 가능.
    """
    listed = {(lane, n) for lane, rows in TABLE.items() for n, *_ in rows}
    opts = {lane: [(n, sc, "표기") for n, sc, red, sub in TABLE[lane]] for lane in LANES}
    cand = {}
    for lane in FLEX_LANES:
        for n, sc, red, sub in TABLE[lane]:
            if sub:
                continue
            for dest in FLEX_LANES:
                if dest != lane and (dest, n) not in listed:
                    cand.setdefault((dest, n), []).append((red, -sc, lane))
    for (dest, n), lst in cand.items():
        red, neg, lane = min(lst)  # 주라인 후보가 둘이면(고락우) 검은 점수 우선
        opts[dest].append((n, -neg, f"이동({lane})"))
    return opts


def find_teams(opts):
    teams = []
    for wonbin_lane in ("탑", "미드"):
        fixed = {wonbin_lane: ("이원빈", 45, "표기"), "원딜": ("김민규", 59.5, "표기")}
        free = [l for l in LANES if l not in fixed]
        pools = [[o for o in opts[l] if o[0] not in ("이원빈", "김민규")] for l in free]
        for combo in product(*pools):
            if len({c[0] for c in combo}) < 3:
                continue
            team = dict(fixed, **dict(zip(free, combo)))
            if abs(sum(v[1] for v in team.values()) - TARGET) < 1e-9:
                teams.append((wonbin_lane, team))
    teams.sort(key=lambda t: (t[0] != "탑", sum(v[2] != "표기" for v in t[1].values()),
                              -t[1]["서폿"][1], t[1]["정글"][0]))
    return teams


# ---------- 엑셀 출력 ----------
FONT = "Arial"
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
LANE_FILL = {"탑": "2F5597", "정글": "C55A11", "미드": "BF9000", "원딜": "00625B", "서폿": "A61C00"}
CENTER = Alignment(horizontal="center", vertical="center")


def header(ws, row, col, text, color="404040"):
    c = ws.cell(row=row, column=col, value=text)
    c.font = Font(name=FONT, bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=color)
    c.alignment = CENTER
    c.border = BORDER
    return c


def write_combo_sheet(ws, teams):
    cols = ["No", "이원빈 라인"]
    for lane in LANES:
        cols += [lane, f"{lane} 점수"]
    cols += ["합계", "라인이동 인원", "라인이동 선수"]
    for i, name in enumerate(cols, 1):
        lane = name.split()[0]
        header(ws, 1, i, name, LANE_FILL.get(lane, "404040"))
    for r, (wl, team) in enumerate(teams, 2):
        moved = [f"{team[l][0]}({team[l][2][3:-1]}→{l})" for l in LANES if team[l][2] != "표기"]
        row = [r - 1, wl]
        for lane in LANES:
            row += [team[lane][0], team[lane][1]]
        row += [f"=D{r}+F{r}+H{r}+J{r}+L{r}", len(moved), ", ".join(moved)]
        for c, v in enumerate(row, 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.font = Font(name=FONT)
            cell.border = BORDER
            if c != len(row):
                cell.alignment = CENTER
            if c in (4, 6, 8, 10, 12, 13):
                cell.number_format = "0.0"
        for lane_i, lane in enumerate(LANES):
            name_cell = ws.cell(row=r, column=3 + lane_i * 2)
            if team[lane][0] in ("이원빈", "김민규"):
                name_cell.font = Font(name=FONT, bold=True)
                name_cell.fill = PatternFill("solid", fgColor="FFF2CC")
            elif team[lane][2] != "표기":
                name_cell.font = Font(name=FONT, color="0070C0", bold=True)
        ws.cell(row=r, column=13).font = Font(name=FONT, bold=True)
    widths = [6, 12] + [10, 9] * 5 + [8, 13, 44]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{max(len(teams) + 1, 2)}"


def main():
    opts = build_options()
    teams = find_teams(opts)
    wb = Workbook()

    # 1) 요약
    ws = wb.active
    ws.title = "요약"
    ws["A1"] = "제19회차 LOLEX 팀 조합 (이원빈 + 김민규 포함, 합계 228점)"
    ws["A1"].font = Font(name=FONT, bold=True, size=14)
    n_top = sum(1 for t in teams if t[0] == "탑")
    n_listed = sum(1 for t in teams if all(v[2] == "표기" for v in t[1].values()))
    last = len(teams) + 1
    rows = [
        ("조건", ""),
        ("목표 합계", TARGET),
        ("고정 멤버 1", "이원빈 — 탑 또는 미드 45점"),
        ("고정 멤버 2", "김민규 — 원딜 59.5점"),
        ("", ""),
        ("결과", ""),
        ("전체 조합 수", f"=COUNTA('전체 조합'!A2:A{last})"),
        ("  이원빈 탑", f"=COUNTIF('전체 조합'!B2:B{last},\"탑\")"),
        ("  이원빈 미드", f"=COUNTIF('전체 조합'!B2:B{last},\"미드\")"),
        ("  라인이동 없이 표기 라인만", f"=COUNTIF('전체 조합'!N2:N{last},0)"),
        ("", ""),
        ("적용한 규칙 (가정 포함)", ""),
        ("1", "이름 앞 #이 붙은 점수는 부라인(고정라인) 점수 → 그 라인으로만 배치."),
        ("2", "#이 없는 탑/정글/미드/원딜 점수는 주라인 점수 → 표에 본인 이름이 없는 다른 라인(탑/정글/미드)으로 같은 점수로 이동 가능."),
        ("3", "이동하려는 라인에 본인 점수가 따로 있으면 그 점수만 사용. 예: 김승환 탑은 #46, 미드는 정글 점수 51."),
        ("4", "서폿 표의 점수는 고정점수 → 서폿 자리에만 사용. 서폿 자리는 서폿 표에 있는 선수만 배치(다른 라인 선수를 서폿으로 돌리는 경우는 제외)."),
        ("5", "주라인 서폿 유저도 # 부라인 점수가 있으면 그 라인으로 배치 가능. 예: 김경환 #정글 43, 류연우 #미드 35.5."),
        ("6", "[가정] 빨간 점수(!)는 라인 제한과 무관한 것으로 보고 #이 없으면 일반 주라인 점수처럼 이동 가능하게 처리."),
        ("7", "[가정] #이 없는데 서폿 표에도 이름이 있는 선수(홍건표·공민석·서필수·김보름·이륜금·이영현·최기쁨·류한별·성기동)는 탑/정글/미드/원딜 쪽을 주라인으로 보고 이동 허용, 서폿은 서폿 점수 사용."),
        ("8", "[가정] 고락우는 # 없이 탑 38.5·정글 41 둘 다 있어, 탑=38.5 / 정글=41 / 미드 이동 시 41(검은 점수)로 처리."),
        ("9", "[가정] 같은 이름은 같은 사람으로 보고 한 팀에 한 번만 배치. 김민규는 원딜 고정이라 다른 선수의 원딜 이동은 없음."),
        ("10", "🔶 아이콘, ^(패치 변경) 표시는 점수 계산에 영향 없는 것으로 처리."),
        ("", ""),
        ("보는 법", ""),
        ("파란 굵은 이름", "주라인이 아닌 라인으로 이동 배치된 선수. '라인이동 선수' 열에 (원라인→배치라인) 표기."),
        ("노란 칸", "고정 멤버(이원빈, 김민규)."),
        ("필터", "'전체 조합' 시트 머리글의 필터로 선수·라인이동 인원(0 = 표기 라인만) 등을 골라 볼 수 있음."),
        ("점수 출처", "사용자가 보낸 '제19회차 LOLEX 임시점수측정표' 이미지를 옮겨 적음 → '점수표' 시트에서 원본과 대조 필요."),
    ]
    for i, (a, b) in enumerate(rows, 3):
        ca, cb = ws.cell(row=i, column=1, value=a), ws.cell(row=i, column=2, value=b)
        ca.font = Font(name=FONT, bold=(b == "" and a != ""))
        cb.font = Font(name=FONT)
        cb.alignment = Alignment(wrap_text=True, vertical="top", horizontal="left")
        ca.alignment = Alignment(vertical="top")
    ws["B4"].number_format = "0.0"
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 100

    # 2) 조합 시트
    write_combo_sheet(wb.create_sheet("전체 조합"), teams)
    write_combo_sheet(wb.create_sheet("이원빈 탑"), [t for t in teams if t[0] == "탑"])
    write_combo_sheet(wb.create_sheet("이원빈 미드"), [t for t in teams if t[0] == "미드"])

    # 3) 점수표 (이미지 전사본)
    ws = wb.create_sheet("점수표")
    for li, lane in enumerate(LANES):
        c0 = 1 + li * 4
        ws.merge_cells(start_row=1, start_column=c0, end_row=1, end_column=c0 + 2)
        header(ws, 1, c0, lane, LANE_FILL[lane])
        for j, h in enumerate(["이름", "점수", "구분"]):
            header(ws, 2, c0 + j, h, "7F7F7F")
        for r, (n, sc, red, sub) in enumerate(TABLE[lane], 3):
            kind = "부라인(#)" if sub else ("서폿 고정" if lane == "서폿" else "주라인")
            for j, v in enumerate([("#" if sub else "") + n, sc, kind]):
                cell = ws.cell(row=r, column=c0 + j, value=v)
                cell.font = Font(name=FONT, color="FF0000" if (red and j == 1) else "000000")
                cell.alignment = CENTER
                cell.border = BORDER
                if j == 1:
                    cell.number_format = "0.0"
        ws.column_dimensions[get_column_letter(c0)].width = 11
        ws.column_dimensions[get_column_letter(c0 + 1)].width = 8
        ws.column_dimensions[get_column_letter(c0 + 2)].width = 16
        ws.column_dimensions[get_column_letter(c0 + 3)].width = 3
    ws.freeze_panes = "A3"

    wb.save(OUT)
    print(len(teams), "teams | 이원빈 탑:", n_top, "| 미드:", len(teams) - n_top, "| 표기 라인만:", n_listed)


if __name__ == "__main__":
    main()
