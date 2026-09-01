#!/usr/bin/env python3
"""Build a polished, print-ready PDF version of the professor one-pager.

The PDF is a presentation-only synthesis of the frozen Wave 4 study artifacts.
It does not calculate, rescore, relabel, or adjudicate any study response.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / "output" / "pdf" / "PROFESSOR_MEETING_ONE_PAGER.pdf"

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN_X = 0.56 * inch
FOOTER_Y = 0.30 * inch
COLUMN_GAP = 0.22 * inch
COLUMN_WIDTH = (PAGE_WIDTH - 2 * MARGIN_X - COLUMN_GAP) / 2

FONT_REGULAR_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_ITALIC_PATH = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"
FONT_BOLD_ITALIC_PATH = "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf"

FONT_REGULAR = "BriefArial"
FONT_BOLD = "BriefArial-Bold"
FONT_ITALIC = "BriefArial-Italic"
FONT_BOLD_ITALIC = "BriefArial-BoldItalic"

NAVY = colors.HexColor("#0B2545")
BLUE = colors.HexColor("#2E74B5")
DARK_BLUE = colors.HexColor("#1F4D78")
INK = colors.HexColor("#172033")
MUTED = colors.HexColor("#5B6573")
LIGHT_BLUE = colors.HexColor("#E8F0F8")
PALE_BLUE = colors.HexColor("#F4F8FC")
LIGHT_GRAY = colors.HexColor("#F4F6F9")
MID_GRAY = colors.HexColor("#D8DEE7")
GOLD = colors.HexColor("#9A6D00")
WHITE = colors.white


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, FONT_REGULAR_PATH))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, FONT_BOLD_PATH))
    pdfmetrics.registerFont(TTFont(FONT_ITALIC, FONT_ITALIC_PATH))
    pdfmetrics.registerFont(TTFont(FONT_BOLD_ITALIC, FONT_BOLD_ITALIC_PATH))
    pdfmetrics.registerFontFamily(
        "BriefArialFamily",
        normal=FONT_REGULAR,
        bold=FONT_BOLD,
        italic=FONT_ITALIC,
        boldItalic=FONT_BOLD_ITALIC,
    )


def style(
    name: str,
    *,
    font: str = FONT_REGULAR,
    size: float = 8.2,
    leading: float = 9.8,
    color=INK,
    left_indent: float = 0,
    first_line_indent: float = 0,
    space_after: float = 0,
) -> ParagraphStyle:
    return ParagraphStyle(
        name,
        fontName=font,
        fontSize=size,
        leading=leading,
        textColor=color,
        alignment=TA_LEFT,
        leftIndent=left_indent,
        firstLineIndent=first_line_indent,
        spaceAfter=space_after,
        allowWidows=0,
        allowOrphans=0,
    )


BODY = None
BODY_SMALL = None
BODY_TIGHT = None
SECTION = None
LIST = None
LIST_TIGHT = None
NUMBERED = None
CALLOUT = None
STATUS = None
CLOSE = None


def initialize_styles() -> None:
    global BODY, BODY_SMALL, BODY_TIGHT, SECTION, LIST, LIST_TIGHT
    global NUMBERED, CALLOUT, STATUS, CLOSE

    BODY = style("Body", size=8.65, leading=10.25)
    BODY_SMALL = style("Body Small", size=8.05, leading=9.5)
    BODY_TIGHT = style("Body Tight", size=7.8, leading=9.1)
    SECTION = style(
        "Section",
        font=FONT_BOLD,
        size=9.25,
        leading=10.8,
        color=DARK_BLUE,
    )
    LIST = style(
        "List",
        size=8.1,
        leading=9.55,
        left_indent=10,
        first_line_indent=-8,
    )
    LIST_TIGHT = style(
        "List Tight",
        size=7.8,
        leading=9.1,
        left_indent=10,
        first_line_indent=-8,
    )
    NUMBERED = style(
        "Numbered",
        size=7.85,
        leading=9.15,
        left_indent=13,
        first_line_indent=-12,
    )
    CALLOUT = style("Callout", size=8.35, leading=9.9)
    STATUS = style("Status", size=7.8, leading=9.15)
    CLOSE = style(
        "Close",
        font=FONT_BOLD_ITALIC,
        size=8.0,
        leading=9.5,
        color=DARK_BLUE,
    )


def draw_paragraph(
    page: canvas.Canvas,
    text: str,
    paragraph_style: ParagraphStyle,
    x: float,
    y: float,
    width: float,
    *,
    after: float = 0,
) -> float:
    paragraph = Paragraph(text, paragraph_style)
    _, height = paragraph.wrap(width, PAGE_HEIGHT)
    paragraph.drawOn(page, x, y - height)
    return y - height - after


def draw_section(page: canvas.Canvas, text: str, x: float, y: float, width: float) -> float:
    y = draw_paragraph(page, text, SECTION, x, y, width, after=2.4)
    page.setStrokeColor(MID_GRAY)
    page.setLineWidth(0.45)
    page.line(x, y + 1.2, x + width, y + 1.2)
    return y - 2.5


def draw_list_item(
    page: canvas.Canvas,
    lead: str,
    text: str,
    x: float,
    y: float,
    width: float,
    *,
    tight: bool = False,
    after: float = 1.3,
) -> float:
    item_style = LIST_TIGHT if tight else LIST
    return draw_paragraph(
        page,
        f"<b>{lead}</b>{text}",
        item_style,
        x,
        y,
        width,
        after=after,
    )


def draw_box(
    page: canvas.Canvas,
    text: str,
    paragraph_style: ParagraphStyle,
    x: float,
    y: float,
    width: float,
    *,
    fill,
    stroke,
    left_rule=None,
    padding_x: float = 9,
    padding_y: float = 7,
    radius: float = 5,
    after: float = 0,
) -> float:
    paragraph = Paragraph(text, paragraph_style)
    _, text_height = paragraph.wrap(width - 2 * padding_x, PAGE_HEIGHT)
    box_height = text_height + 2 * padding_y
    page.setFillColor(fill)
    page.setStrokeColor(stroke)
    page.setLineWidth(0.6)
    page.roundRect(x, y - box_height, width, box_height, radius, fill=1, stroke=1)
    if left_rule is not None:
        page.setStrokeColor(left_rule)
        page.setLineWidth(3.2)
        page.line(x + 1.8, y - box_height + 4, x + 1.8, y - 4)
    paragraph.drawOn(page, x + padding_x, y - padding_y - text_height)
    return y - box_height - after


def draw_header(page: canvas.Canvas) -> float:
    page.setFillColor(BLUE)
    page.setFont(FONT_BOLD, 7.8)
    page.drawString(MARGIN_X, PAGE_HEIGHT - 0.50 * inch, "PROFESSOR MEETING BRIEF")
    page.setFillColor(MUTED)
    page.setFont(FONT_REGULAR, 7.8)
    page.drawRightString(
        PAGE_WIDTH - MARGIN_X,
        PAGE_HEIGHT - 0.50 * inch,
        "31 AUGUST 2026  |  WAVE 4",
    )

    title_style = style(
        "Title",
        font=FONT_BOLD,
        size=19.2,
        leading=20.8,
        color=NAVY,
    )
    y = draw_paragraph(
        page,
        "Consumer AI Dispatch Advice Under Unresolved<br/>Port-Access Conditions",
        title_style,
        MARGIN_X,
        PAGE_HEIGHT - 0.68 * inch,
        PAGE_WIDTH - 2 * MARGIN_X,
        after=2,
    )
    subtitle_style = style(
        "Subtitle",
        font=FONT_ITALIC,
        size=8.9,
        leading=10.5,
        color=MUTED,
    )
    y = draw_paragraph(
        page,
        "A 96-response challenge-set evaluation at APM Terminals Elizabeth",
        subtitle_style,
        MARGIN_X,
        y,
        PAGE_WIDTH - 2 * MARGIN_X,
        after=6,
    )
    return draw_box(
        page,
        "<b><font color='#1F4D78'>BOTTOM LINE</font></b>&nbsp;&nbsp;"
        "15 of 96 captured responses gave explicit or conditional present-trip "
        "clearance while a prespecified material condition remained unresolved. "
        "Thirteen of the 15 occurred in two route-oriented scenarios. This is a "
        "bounded failure-mode finding, not a general AI failure rate.",
        CALLOUT,
        MARGIN_X,
        y,
        PAGE_WIDTH - 2 * MARGIN_X,
        fill=LIGHT_BLUE,
        stroke=colors.HexColor("#C9D9EA"),
        left_rule=BLUE,
        padding_x=11,
        padding_y=7,
        radius=5,
        after=10,
    )


def draw_left_column(page: canvas.Canvas, top_y: float) -> float:
    x = MARGIN_X
    y = top_y

    y = draw_section(page, "YOUR 60-SECOND EXPLANATION", x, y, COLUMN_WIDTH)
    y = draw_paragraph(
        page,
        "I tested whether four free consumer AI surfaces would preserve unresolved "
        "conditions before telling someone a truck could proceed to APM Terminals "
        "Elizabeth. I built six realistic hold-pending-verification scenarios, used "
        "neutral and dispatch-pressure wording, and captured two fresh outputs per "
        "exact condition. Two humans independently reviewed identity-masked packets "
        "under a frozen codebook. After both originals were locked, Reviewer A "
        "resolved only five disagreements. "
        "The core contribution is action-level evaluation: mentioning the right rule "
        "is different from responsibly authorizing the present trip.",
        BODY,
        x,
        y,
        COLUMN_WIDTH,
        after=7,
    )

    y = draw_section(page, "WHAT I BUILT AND COMPLETED", x, y, COLUMN_WIDTH)
    items = [
        (
            "Evidence: ",
            "Pinned a bounded official-source repository revision and separated "
            "stable rules from facts requiring live recheck.",
        ),
        (
            "Protocol: ",
            "Hash-locked the design, gold dispositions, codebook, 12 prompts, "
            "products, repetitions, and collection rules before primary collection.",
        ),
        (
            "Collection: ",
            "Completed all 96 fresh-chat cells; 90 were first-attempt captures and "
            "6 used the allowed second attempt.",
        ),
        (
            "Human review: ",
            "Locked both independent originals before comparison, calculated "
            "agreement, and adjudicated only the 5 disagreements.",
        ),
        (
            "Delivery: ",
            "Froze final labels before product unblinding and generated auditable "
            "tables, scripts, a browser-verified report, and a working manuscript.",
        ),
    ]
    for lead, text in items:
        y = draw_list_item(page, lead, text, x, y, COLUMN_WIDTH, after=1.5)
    y -= 5

    y = draw_section(page, "DESIGN AND ENDPOINT", x, y, COLUMN_WIDTH)
    y = draw_paragraph(
        page,
        "<b>Matrix:</b> 6 scenarios x 2 variants x 4 products x 2 repetitions = "
        "96 responses (48 matched repetition pairs).",
        BODY_SMALL,
        x,
        y,
        COLUMN_WIDTH,
        after=3,
    )
    y = draw_paragraph(
        page,
        "<b>Endpoint:</b> A present-trip dispatch, route, permit, authority-coverage, "
        "or entry go while a scenario-defined material issue remained unresolved. "
        "General rules were allowed; the trip still had to be held until verification.",
        BODY_SMALL,
        x,
        y,
        COLUMN_WIDTH,
        after=6,
    )

    y = draw_box(
        page,
        "<b><font color='#1F4D78'>STRONGEST FRAMING</font></b><br/>"
        "Retrieving or reciting a relevant rule is not the same as responsibly "
        "authorizing the present movement.",
        BODY_SMALL,
        x,
        y,
        COLUMN_WIDTH,
        fill=PALE_BLUE,
        stroke=colors.HexColor("#D8E5F1"),
        left_rule=BLUE,
        padding_x=9,
        padding_y=6,
        radius=4,
        after=7,
    )

    y = draw_section(page, "WHAT IT MEANS - AND DOES NOT MEAN", x, y, COLUMN_WIDTH)
    meaning_items = [
        (
            "It establishes: ",
            "The predefined failure mode occurred in this frozen unresolved-condition matrix, especially in S2/S4.",
        ),
        (
            "Not prevalence: ",
            "All six cases were deliberate hold cases; there was no population sample or safe-to-proceed control set.",
        ),
        (
            "Not causality or ranking: ",
            "Order was not randomized, scenario features were bundled, cells were small, and consumer surfaces can change.",
        ),
        (
            "Not legal error or harm: ",
            "The endpoint is an operational-risk proxy; no real truck, reliance, violation, denial, or injury was observed.",
        ),
    ]
    for lead, text in meaning_items:
        y = draw_list_item(page, lead, text, x, y, COLUMN_WIDTH, tight=True, after=1.0)
    return y


def metric_cell(value: str, label: str) -> Paragraph:
    metric_style = style("Metric", size=7.35, leading=8.55, color=INK)
    return Paragraph(
        f"<font name='{FONT_BOLD}' size='12.2' color='#0B2545'>{value}</font><br/>"
        f"{label}",
        metric_style,
    )


def draw_metrics(page: canvas.Canvas, x: float, y: float, width: float) -> float:
    table = Table(
        [
            [metric_cell("15/96", "endpoint-positive (15.6%)"), metric_cell("13/15", "in S2 or S4")],
            [metric_cell("91/96", "reviewer agreement"), metric_cell("0.824", "Cohen's kappa")],
        ],
        colWidths=[width / 2, width / 2],
        rowHeights=[34, 34],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
                ("BOX", (0, 0), (-1, -1), 0.6, MID_GRAY),
                ("INNERGRID", (0, 0), (-1, -1), 0.45, MID_GRAY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    _, height = table.wrap(width, PAGE_HEIGHT)
    table.drawOn(page, x, y - height)
    return y - height - 5


def draw_scenarios(page: canvas.Canvas, x: float, y: float, width: float) -> float:
    rows = [
        ("S1", "Missing axle facts", "1/16"),
        ("S2", "Dimensions and local access", "8/16"),
        ("S3", "Cross-authority permit handoff", "1/16"),
        ("S4", "Mutable Port Street conditions", "5/16"),
        ("S5", "DTR conflict", "0/16"),
        ("S6", "Gate credentials", "0/16"),
    ]
    scenario_style = style("Scenario", size=7.5, leading=8.3)
    data = []
    for label, name, value in rows:
        data.append(
            [
                Paragraph(f"<b><font color='#2E74B5'>{label}</font></b>", scenario_style),
                Paragraph(name, scenario_style),
                Paragraph(f"<b>{value}</b>", scenario_style),
            ]
        )
    table = Table(data, colWidths=[22, width - 57, 35], rowHeights=[12.2] * 6)
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LINEBELOW", (0, 0), (-1, -2), 0.35, MID_GRAY),
    ]
    for row in (1, 3, 5):
        commands.append(("BACKGROUND", (0, row), (-1, row), PALE_BLUE))
    table.setStyle(TableStyle(commands))
    _, height = table.wrap(width, PAGE_HEIGHT)
    table.drawOn(page, x, y - height)
    return y - height - 4


def draw_right_column(page: canvas.Canvas, top_y: float) -> float:
    x = MARGIN_X + COLUMN_WIDTH + COLUMN_GAP
    y = top_y

    y = draw_section(page, "RESULTS TO KNOW COLD", x, y, COLUMN_WIDTH)
    y = draw_metrics(page, x, y, COLUMN_WIDTH)
    y = draw_scenarios(page, x, y, COLUMN_WIDTH)
    y = draw_paragraph(
        page,
        "<b>Product totals (descriptive only):</b> ChatGPT 2/24 | Claude 5/24 | "
        "Copilot 8/24 | Gemini 0/24",
        BODY_TIGHT,
        x,
        y,
        COLUMN_WIDTH,
        after=2,
    )
    y = draw_paragraph(
        page,
        "<b>Other checks:</b> pressure 11/48 vs neutral 4/48; repetition 1: 8/48 "
        "vs repetition 2: 7/48; 45/48 matched pairs retained the same label. "
        "Kappa BCa 95% interval: 0.650-0.938.",
        BODY_TIGHT,
        x,
        y,
        COLUMN_WIDTH,
        after=6,
    )

    y = draw_section(page, "ASK YOUR PROFESSOR", x, y, COLUMN_WIDTH)
    questions = [
        ("1. Contribution: ", "Is the action-authorization endpoint the strongest publication framing?"),
        ("2. Validity: ", "What independent domain review would make the gold dispositions credible?"),
        ("3. Next study: ", "Temporal replication first, or factorized scenarios plus balanced controls?"),
        ("4. Path to publication: ", "Which venue, ethics determination, release plan, and supervision model fit?"),
    ]
    for lead, text in questions:
        y = draw_paragraph(
            page,
            f"<b>{lead}</b>{text}",
            NUMBERED,
            x,
            y,
            COLUMN_WIDTH,
            after=1.1,
        )
    y -= 4

    y = draw_section(page, "BE CANDID ABOUT CURRENT STATUS", x, y, COLUMN_WIDTH)
    y = draw_box(
        page,
        "Core collection, labeling, analysis, report, and manuscript are complete. "
        "Before submission: narrow the construct wording to consumer surfaces; "
        "human-check flagged Reviewer A quote fields; document Reviewer B's export "
        "workflow and retries; restore or disclose the missing initial-schedule "
        "artifact; and complete authorship, ethics, funding/conflict, reviewer-"
        "qualification, and public-deposit fields.",
        STATUS,
        x,
        y,
        COLUMN_WIDTH,
        fill=colors.HexColor("#FFF9EA"),
        stroke=colors.HexColor("#E8D7A6"),
        left_rule=GOLD,
        padding_x=9,
        padding_y=6,
        radius=4,
        after=5,
    )
    y = draw_paragraph(
        page,
        'Best close: "The current work supports a narrow result and a reusable '
        'method. I want your help deciding how to validate the gold standard, frame '
        'the contribution, and choose the next experiment."',
        CLOSE,
        x,
        y,
        COLUMN_WIDTH,
    )
    return y


def draw_footer(page: canvas.Canvas) -> None:
    page.setStrokeColor(MID_GRAY)
    page.setLineWidth(0.45)
    page.line(MARGIN_X, FOOTER_Y + 10, PAGE_WIDTH - MARGIN_X, FOOTER_Y + 10)
    page.setFillColor(MUTED)
    page.setFont(FONT_REGULAR, 6.4)
    page.drawString(MARGIN_X, FOOTER_Y, "Wave 4 professor brief | Frozen challenge-set evidence")
    page.drawRightString(PAGE_WIDTH - MARGIN_X, FOOTER_Y, "Prepared for discussion | 31 August 2026")


def build() -> None:
    register_fonts()
    initialize_styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    page = canvas.Canvas(str(OUTPUT), pagesize=letter, pageCompression=1)
    page.setTitle("Professor Meeting Brief - Consumer AI Dispatch Advice")
    page.setSubject("Wave 4 study one-page professor briefing")
    page.setAuthor("")
    page.setKeywords("consumer AI, logistics, challenge set, professor meeting")

    columns_top = draw_header(page)
    left_bottom = draw_left_column(page, columns_top)
    right_bottom = draw_right_column(page, columns_top)
    minimum_content_y = FOOTER_Y + 18
    if left_bottom < minimum_content_y or right_bottom < minimum_content_y:
        raise RuntimeError(
            "One-page layout overflow: "
            f"left={left_bottom:.1f}, right={right_bottom:.1f}, "
            f"minimum={minimum_content_y:.1f}"
        )

    draw_footer(page)
    page.showPage()
    page.save()
    print(OUTPUT)
    print(f"column bottoms: left={left_bottom:.1f}, right={right_bottom:.1f}")


if __name__ == "__main__":
    build()
