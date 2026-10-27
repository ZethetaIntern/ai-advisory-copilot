"""
Generate Professional 10-Slide Presentation Deck (.pptx)
scripts/generate_deck.py

Uses python-pptx to generate an institutional-grade, 16:9 widescreen presentation deck
for the Zeckathon PS04 AI Advisory Co-pilot project.
"""
import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Color Palette (Institutional Navy, Emerald Green, Amber Gold, Slate Gray)
NAVY = RGBColor(15, 23, 42)         # #0f172a
DEEP_BLUE = RGBColor(30, 58, 138)    # #1e3a8a
LIGHT_BG = RGBColor(248, 250, 252)   # #f8fafc
CARD_BG = RGBColor(255, 255, 255)    # #ffffff
CARD_BORDER = RGBColor(226, 232, 240)# #e2e8f0
TEXT_DARK = RGBColor(30, 41, 59)     # #1e293b
TEXT_MUTED = RGBColor(100, 116, 139) # #64748b
EMERALD = RGBColor(16, 185, 129)     # #10b981
AMBER = RGBColor(217, 119, 6)        # #d97706
CRIMSON = RGBColor(220, 38, 38)      # #dc2626
WHITE = RGBColor(255, 255, 255)      # #ffffff


def create_deck(output_path: str = "reports/presentation_deck.pptx"):
    prs = Presentation()
    # Set 16:9 widescreen dimensions (13.33 x 7.5 inches)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_bg(slide, color):
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = color
        shape.line.color.rgb = color
        return shape

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        return card

    def add_header(slide, title_text, category_text="ZECKATHON PS04: AI ADVISORY CO-PILOT"):
        # Header category pill
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = DEEP_BLUE

        # Main slide title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY

    # ==========================================
    # SLIDE 1: TITLE SLIDE (Dark Navy)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, NAVY)

    # Title & Subtitle in single block
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(3.0))
    tf1 = t_box.text_frame
    tf1.word_wrap = True

    p1 = tf1.paragraphs[0]
    p1.text = "AI Advisory Co-pilot for SEBI RIA"
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_after = Pt(14)

    p2 = tf1.add_paragraph()
    p2.text = "Fiduciary-Grade, Deterministic, Zero-Hallucination Decision Support System"
    p2.font.size = Pt(20)
    p2.font.color.rgb = RGBColor(147, 197, 253)
    p2.space_after = Pt(24)

    p3 = tf1.add_paragraph()
    p3.text = "Core Rule: The LLM explains; Python computes. The adviser governs; the client is protected."
    p3.font.size = Pt(15)
    p3.font.italic = True
    p3.font.color.rgb = RGBColor(226, 232, 240)

    # 4 Metric badges at bottom
    metrics = [
        ("73 / 73", "Pytest Suite (100%)", EMERALD),
        ("100.0%", "RAG Accuracy (25/25)", EMERALD),
        ("0.0%", "Hallucination Rate", AMBER),
        ("100.0%", "Adversarial Defense (30/30)", EMERALD),
    ]
    for i, (val, label, col) in enumerate(metrics):
        card = add_card(s1, Inches(1.0 + i * 2.85), Inches(5.2), Inches(2.7), Inches(1.4), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
        c_box = s1.shapes.add_textbox(Inches(1.1 + i * 2.85), Inches(5.3), Inches(2.5), Inches(1.2))
        tf = c_box.text_frame
        p_val = tf.paragraphs[0]
        p_val.text = val
        p_val.font.size = Pt(26)
        p_val.font.bold = True
        p_val.font.color.rgb = col
        p_lbl = tf.add_paragraph()
        p_lbl.text = label
        p_lbl.font.size = Pt(11)
        p_lbl.font.color.rgb = RGBColor(203, 213, 225)

    # ==========================================
    # SLIDE 2: THE PROBLEM (The RIA Dilemma)
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2, LIGHT_BG)
    add_header(s2, "The Problem: Scaling Advisory vs Fiduciary Strictness")

    card_left = add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    tb_l = s2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "The Scale & Compliance Bottleneck"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = CRIMSON
    p.space_after = Pt(12)

    bullets_l = [
        "Massive Shortage: Under 1,300 active RIAs serving India's 1.4 Billion population.",
        "Manual Overhead: Constructing customized goal plans, SIP schedules, and glide paths takes 4-6 hours per client.",
        "Perils of Generic LLMs: Fabricate NAVs, hallucinate expense ratios, and hallucinate return promises—a direct SEBI regulatory violation.",
        "Compliance Liability: SEBI Investment Advisers Regulations (2013) impose strict fiduciary liability on client suitability and disclosures.",
    ]
    for b in bullets_l:
        p = tf_l.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(10)

    card_right = add_card(s2, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0))
    tb_r = s2.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.2), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "Our Architectural Solution"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    p.space_after = Pt(12)

    bullets_r = [
        "Deterministic Math Engine: Every rupee, SIP, CAGR, and drawdown comes from closed-form Python code, never prompt generation.",
        "Anti-Hallucination Verifier: Verifies every claimed number against verbatim factsheet chunk text. Refuses if ungrounded.",
        "Code-Enforced Approval Gate: State machine ensures no report or PDF reaches a client without explicit adviser review and sign-off.",
        "Regulatory Suitability: Automated SEBI Regulation 17 rules protect vulnerable clients from unsuitable high-risk products.",
    ]
    for b in bullets_r:
        p = tf_r.add_paragraph()
        p.text = "✓ " + b
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(10)

    # ==========================================
    # SLIDE 3: SYSTEM ARCHITECTURE
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3, LIGHT_BG)
    add_header(s3, "System Architecture: Dual-Engine Blueprint")

    modules = [
        ("1. Risk Profiler", "Objective Capacity (0-100)\nBehavioural Tolerance (0-100)\nConflict rule: min(Cap, Tol)\nAdviser mismatch alerts", DEEP_BLUE),
        ("2. Goal Planner", "Compound inflation (6%, 10%, 9%)\nFV of Annuity Due SIP\n10% Step-Up SIP schedule\nLinear Glide Path\n3-Bucket Retiree model", DEEP_BLUE),
        ("3. Portfolio Engine", "Direct + Growth filter only\nMulti-factor scoring (TER, Sharpe)\nTop 1-2 shortlisted funds\n10Y backtest vs benchmark\nSurvivorship caveats", DEEP_BLUE),
        ("4. RAG & Verifier", "SQLite Fact Table first\nBM25 + Dense Semantic RRF\nStrict Anti-Hallucination Verifier\nVerbatim [Doc, p.X] citation\nRefuses guessing", DEEP_BLUE),
        ("5. Guardrails", "Input guarantee interceptor\nPrompt injection defense\nSEBI Reg 17 suitability\nOutput promise scanner\n5 Mandatory disclosures", DEEP_BLUE),
        ("6. Approval Gate", "State machine (DRAFT->APP)\nImmutable audit trail log\nCode-enforced PDF block\nInstitutional client export\nFastAPI + Streamlit UI", DEEP_BLUE),
    ]

    for i, (title, desc, col) in enumerate(modules):
        col_idx = i % 3
        row_idx = i // 3
        left = Inches(0.8 + col_idx * 3.9)
        top = Inches(1.8 + row_idx * 2.6)
        add_card(s3, left, top, Inches(3.7), Inches(2.4))
        tb = s3.shapes.add_textbox(left + Inches(0.15), top + Inches(0.15), Inches(3.4), Inches(2.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = col
        p_t.space_after = Pt(6)

        for line in desc.split("\n"):
            p_d = tf.add_paragraph()
            p_d.text = "• " + line
            p_d.font.size = Pt(11)
            p_d.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 4: RISK PROFILING
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4, LIGHT_BG)
    add_header(s4, "Deterministic Risk Profiling & Conflict Resolution")

    # Left: Explanation
    add_card(s4, Inches(0.8), Inches(1.8), Inches(4.5), Inches(5.0))
    tb_exp = s4.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(4.1), Inches(4.6))
    tf_exp = tb_exp.text_frame
    tf_exp.word_wrap = True
    p = tf_exp.paragraphs[0]
    p.text = "Dual-Axis Assessment Model"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = DEEP_BLUE
    p.space_after = Pt(8)

    pts = [
        "Risk Capacity (0-100): Income stability (20%), horizon (25%), liabilities ratio (20%), dependants (15%), emergency fund (20%), and human capital life stage.",
        "Risk Tolerance (0-100): 8 psychometric questions + behavioural penalties for F&O derivatives and past panic selling.",
        "Governing Band: min(Capacity, Tolerance). Always assigns the conservative boundary.",
        "Adviser Review Trigger: If capacity and tolerance differ by >1 band, sets needs_adviser_review=True with natural language diagnosis.",
    ]
    for pt in pts:
        p = tf_exp.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # Right: Results Table on 6 Personas
    add_card(s4, Inches(5.6), Inches(1.8), Inches(6.9), Inches(5.0))
    tb_tab = s4.shapes.add_textbox(Inches(5.8), Inches(2.0), Inches(6.5), Inches(4.6))
    tf_tab = tb_tab.text_frame
    tf_tab.word_wrap = True
    p = tf_tab.paragraphs[0]
    p.text = "Deterministic Persona Results"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    persona_rows = [
        ("Arjun Mehta (23, Grad)", "80.2 / 100", "72.5 / 100", "Moderate", "Aligned"),
        ("Priya & Rahul (31, Couple)", "78.2 / 100", "67.5 / 100", "Mod. Aggressive", "Aligned"),
        ("Ketan Patel (44, Business)", "65.0 / 100", "32.5 / 100", "Mod. Conservative", "⚠️ Review Required"),
        ("Dr. Sneha Kumar (38, Doctor)", "79.2 / 100", "31.2 / 100", "Mod. Conservative", "⚠️ Review Required"),
        ("V. Sundararajan (68, Retiree)", "52.2 / 100", "25.0 / 100", "Mod. Conservative", "Decumulation Cap"),
        ("Vikram Desai (29, Trader)", "48.2 / 100", "37.5 / 100", "Mod. Conservative", "F&O Penalty Flag"),
    ]
    for name, cap, tol, band, rev in persona_rows:
        p = tf_tab.add_paragraph()
        p.text = f"{name}: Cap {cap} | Tol {tol} -> {band} [{rev}]"
        p.font.size = Pt(11)
        p.font.bold = ("Review" in rev or "Penalty" in rev)
        p.font.color.rgb = CRIMSON if "Review" in rev else TEXT_DARK
        p.space_after = Pt(6)

    # ==========================================
    # SLIDE 5: GOAL PLANNER & GLIDE PATH
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5, LIGHT_BG)
    add_header(s5, "Goal-Based Financial Planner & Dynamic Glide Path")

    # 3 Feature Cards
    cards_s5 = [
        ("1. Dynamic Inflation Adjustment", "Future Cost: FV = PV * (1 + i)^n\n\n• General CPI: 6% p.a.\n• Higher Education: 10% p.a.\n• Healthcare/Medical: 9% p.a.\n\nAll rates configurable & fully disclosed.", DEEP_BLUE),
        ("2. Precision SIP Formulas", "Monthly Flat SIP via Annuity Due:\nPMT = FV * r_m / [((1+r_m)^N - 1)(1+r_m)]\n\nStep-Up SIP (10% Annual Escalation):\n• Starts lower to match early career cashflows\n• Escalates annually with income growth.", DEEP_BLUE),
        ("3. Linear Glide Path & 3-Bucket", "Linear Glide Path:\n• Shifts equity to debt over final 5 years before goal maturity.\n\nRetiree 3-Bucket Model (25y Horizon):\n• Bucket 1: 2y Cash (Immediate draw)\n• Bucket 2: 4y Debt (Stable refill)\n• Bucket 3: Growth Equity (Beat inflation)", DEEP_BLUE),
    ]
    for i, (title, desc, col) in enumerate(cards_s5):
        left = Inches(0.8 + i * 3.9)
        add_card(s5, left, Inches(1.8), Inches(3.7), Inches(5.0))
        tb = s5.shapes.add_textbox(left + Inches(0.2), Inches(2.0), Inches(3.3), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(10)
        for line in desc.split("\n"):
            p_l = tf.add_paragraph()
            p_l.text = line
            p_l.font.size = Pt(12)
            p_l.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 6: FUND SELECTION & BACKTEST
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6, LIGHT_BG)
    add_header(s6, "Direct Fund Selection Engine & 10-Year Backtest")

    add_card(s6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    tb_sc = s6.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.6))
    tf_sc = tb_sc.text_frame
    tf_sc.word_wrap = True
    p = tf_sc.paragraphs[0]
    p.text = "Transparent Multi-Factor Scoring (100 Pts)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = DEEP_BLUE
    p.space_after = Pt(10)

    weights_info = [
        ("Return Consistency (30%)", "3Y and 5Y rolling CAGR"),
        ("Risk-Adjusted Return (25%)", "Sharpe Ratio (Rf = 6.5% T-Bill benchmark)"),
        ("Downside Protection (20%)", "Maximum Peak-to-Trough Drawdown"),
        ("Low Expense Ratio (15%)", "Direct Plan TER (saves 0.7-1.0% recurring)"),
        ("AUM & Manager Tenure (10%)", "High liquidity (>10k Cr) and tenured manager"),
    ]
    for w, d in weights_info:
        p = tf_sc.add_paragraph()
        p.text = f"• {w}: {d}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(4)

    p_note = tf_sc.add_paragraph()
    p_note.text = "\nSelection Rationale: Every recommendation automatically details TER, tenure, and performance reasons."
    p_note.font.size = Pt(11)
    p_note.font.italic = True
    p_note.font.color.rgb = TEXT_MUTED

    add_card(s6, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0))
    tb_bt = s6.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.2), Inches(4.6))
    tf_bt = tb_bt.text_frame
    tf_bt.word_wrap = True
    p = tf_bt.paragraphs[0]
    p.text = "10-Year Historical Backtest Simulation"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    bt_pts = [
        "Annual Rebalancing: Rebalances annually back to target asset allocation weights.",
        "Composite Benchmark: Compared against 65:35 Equity/Debt composite benchmark.",
        "Reported Metrics: Exact CAGR, Volatility, Max Drawdown, and Sharpe Ratio.",
        "Mandatory Disclosures Included:",
        "  - Survivorship bias warning",
        "  - Direct plan inception date limit (Jan 2013)",
        "  - Past performance caveat (not indicative of future returns)",
    ]
    for pt in bt_pts:
        p = tf_bt.add_paragraph()
        p.text = pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(4)

    # ==========================================
    # SLIDE 7: RAG RESEARCH ASSISTANT & VERIFIER
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7, LIGHT_BG)
    add_header(s7, "Research Assistant with Verifier (100% Benchmark Score)")

    # 4 Metric Cards across top
    rag_metrics = [
        ("100.0%", "Accuracy (25/25)", EMERALD),
        ("100.0%", "Citation Rate (Factuals)", EMERALD),
        ("100.0%", "Refusal Rate (Attacks)", EMERALD),
        ("0.0%", "Hallucination Rate", AMBER),
    ]
    for i, (val, lbl, col) in enumerate(rag_metrics):
        card = add_card(s7, Inches(0.8 + i * 2.95), Inches(1.8), Inches(2.8), Inches(1.3))
        tb = s7.shapes.add_textbox(Inches(0.9 + i * 2.95), Inches(1.9), Inches(2.6), Inches(1.1))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = col
        p_l = tf.add_paragraph()
        p_l.text = lbl
        p_l.font.size = Pt(11)
        p_l.font.color.rgb = TEXT_MUTED

    # Bottom Architecture Card
    add_card(s7, Inches(0.8), Inches(3.3), Inches(11.6), Inches(3.5))
    tb_pipe = s7.shapes.add_textbox(Inches(1.0), Inches(3.5), Inches(11.2), Inches(3.1))
    tf_pipe = tb_pipe.text_frame
    tf_pipe.word_wrap = True
    p = tf_pipe.paragraphs[0]
    p.text = "Two-Stage Retrieval + Anti-Hallucination Verifier Pipeline"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = DEEP_BLUE
    p.space_after = Pt(8)

    pipe_steps = [
        "1. First Router (SQLite Fact Table): Direct lookups (TER, exit load, benchmark, min SIP, AUM, manager tenure) resolve in O(1) time directly from verified SQLite table with document coordinates.",
        "2. Hybrid Retrieval (BM25 + Dense Semantic): Multi-hop queries retrieve top page chunks via Reciprocal Rank Fusion (RRF), preserving exact page numbers.",
        "3. Strict Verifier: Regex entity extractor parses all numbers, percentages, and entities in candidate answer. If ANY number does not appear verbatim in the cited page text, the answer is replaced with: 'Not found in the provided sources.'",
        "4. Never Guess: Zero reliance on model memory. Refusing is explicitly prioritized over guessing.",
    ]
    for stp in pipe_steps:
        p = tf_pipe.add_paragraph()
        p.text = stp
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(4)

    # ==========================================
    # SLIDE 8: GUARDRAILS & SUITABILITY
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8, LIGHT_BG)
    add_header(s8, "Multi-Layer Guardrails & Suitability Engine")

    cards_s8 = [
        ("Input Guardrail Layer", "Intercepts adversarial prompts before model inference:\n\n• Return Guarantees: 'guarantee 20%', 'double money', 'risk-free'\n• Prompt Injections: 'ignore instructions', 'DAN mode', system overrides\n• Bypass Attempts: 'skip approval', 'send directly to client'\n\n30/30 Attacks Neutralized (100% Defense).", CRIMSON),
        ("SEBI Reg 17 Suitability", "Rules-based suitability checks:\n\n• Senior Citizens (>60): Excessive equity (>40%) and small caps are BLOCKED.\n• F&O Traders: Speculative history + panic selling triggers WARNING and conservative index redirection.\n• Low Capacity: High-risk allocations blocked if capacity score < 40.", DEEP_BLUE),
        ("Output Guardrail Layer", "Compliance scanning and statutory disclaimers:\n\n• Promise Scanner: Blocks and replaces any implied return promises.\n• Mandatory SEBI Disclosures:\n  1. Direct Plans Only (No commission)\n  2. Fiduciary Duty & Conflict Statement\n  3. Statutory Mutual Fund Risk Warning\n  4. Past Performance Caveat\n  5. No Return Guarantee Statement", EMERALD),
    ]
    for i, (title, desc, col) in enumerate(cards_s8):
        left = Inches(0.8 + i * 3.9)
        add_card(s8, left, Inches(1.8), Inches(3.7), Inches(5.0))
        tb = s8.shapes.add_textbox(left + Inches(0.2), Inches(2.0), Inches(3.3), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(10)
        for line in desc.split("\n"):
            p_l = tf.add_paragraph()
            p_l.text = line
            p_l.font.size = Pt(12)
            p_l.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 9: APPROVAL GATE & PDF EXPORT
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_bg(s9, LIGHT_BG)
    add_header(s9, "Adviser Approval Gate & Client-Ready PDF Export")

    add_card(s9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    tb_st = s9.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.6))
    tf_st = tb_st.text_frame
    tf_st.word_wrap = True
    p = tf_st.paragraphs[0]
    p.text = "Code-Enforced State Machine"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = DEEP_BLUE
    p.space_after = Pt(10)

    st_pts = [
        "State Transition: DRAFT -> PENDING_REVIEW -> APPROVED / REJECTED.",
        "Code-Level Block: export_pdf() checks plan status. If status != APPROVED, raises Python PermissionError.",
        "No Prompt Bypass: Security is enforced at code level, making prompt injection bypasses impossible.",
        "Immutable Audit Log: Records timestamp, adviser ID, previous status, new status, and adviser notes for regulatory inspection.",
    ]
    for pt in st_pts:
        p = tf_st.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    add_card(s9, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0))
    tb_pdf = s9.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.2), Inches(4.6))
    tf_pdf = tb_pdf.text_frame
    tf_pdf.word_wrap = True
    p = tf_pdf.paragraphs[0]
    p.text = "Institutional Client PDF Report"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    p.space_after = Pt(10)

    pdf_pts = [
        "Generated via fpdf2 with professional typography.",
        "Comprehensive Report Sections:",
        "  1. Client Diagnostic & Governing Risk Band",
        "  2. Goal Roadmap & Monthly Flat/Step-Up SIPs",
        "  3. Recommended Direct Mutual Funds with Rationale",
        "  4. 10-Year Backtest & Methodology Limitations",
        "  5. All 5 Mandatory SEBI RIA Disclosures",
        "  6. RIA Digital Sign-Off Box & Audit Log ID",
    ]
    for pt in pdf_pts:
        p = tf_pdf.add_paragraph()
        p.text = pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(4)

    # ==========================================
    # SLIDE 10: CONCLUSION & SUMMARY (Dark Navy)
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_bg(s10, NAVY)

    tb_c = s10.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.3), Inches(5.5))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    p = tf_c.paragraphs[0]
    p.text = "Summary & Production Readiness"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.space_after = Pt(16)

    recap_pts = [
        "100% Deterministic: All math computed in Python. Zero numerical hallucination.",
        "Honest Verifier: 100% accuracy on gold benchmark, 100% page citation, 0 hallucinations.",
        "Regulatory Suitability: Automated SEBI Regulation 17 checks protect vulnerable personas.",
        "Adviser Gate: Institutional state machine guarantees client cannot receive unapproved plans.",
        "One-Command Reproducibility: 'make reproduce' or 'python scripts/reproduce.py' runs all personas, tests, and PDF exports in under 10 seconds.",
    ]
    for pt in recap_pts:
        p = tf_c.add_paragraph()
        p.text = "✓ " + pt
        p.font.size = Pt(15)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_after = Pt(10)

    p_f = tf_c.add_paragraph()
    p_f.text = "\nLive Dashboard: http://localhost:8501  |  REST API: http://localhost:8000"
    p_f.font.size = Pt(14)
    p_f.font.bold = True
    p_f.font.color.rgb = RGBColor(147, 197, 253)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    print(f"Presentation deck successfully created at: {output_path}")
    return output_path


if __name__ == "__main__":
    create_deck()
