"""
resume_builder.py  — Generate a polished PDF resume using ReportLab.
"""
from __future__ import annotations

import io
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ── Colour palette ────────────────────────────────────────────────────────────
_BLUE       = colors.HexColor("#1e40af")
_LIGHT_BLUE = colors.HexColor("#3b82f6")
_DARK       = colors.HexColor("#1e293b")
_GREY       = colors.HexColor("#64748b")
_LIGHT_GREY = colors.HexColor("#f1f5f9")
_WHITE      = colors.white


def generate_resume_pdf(
    name: str,
    email: str,
    phone: str,
    location: str,
    stream: str,
    career: str,
    career_details: dict,
    extra_skills: str = "",
    achievements: str = "",
) -> bytes:
    """
    Build a professional PDF résumé and return it as raw bytes.
    All arguments are plain strings / dicts; no Qt dependency.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    # ── Styles ──────────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()

    s_name = ParagraphStyle(
        "name",
        fontSize=22,
        fontName="Helvetica-Bold",
        textColor=_BLUE,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    s_contact = ParagraphStyle(
        "contact",
        fontSize=9,
        fontName="Helvetica",
        textColor=_GREY,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    s_section = ParagraphStyle(
        "section",
        fontSize=11,
        fontName="Helvetica-Bold",
        textColor=_BLUE,
        spaceBefore=10,
        spaceAfter=3,
    )
    s_body = ParagraphStyle(
        "body",
        fontSize=9.5,
        fontName="Helvetica",
        textColor=_DARK,
        leading=14,
        spaceAfter=2,
    )
    s_bullet = ParagraphStyle(
        "bullet",
        fontSize=9.5,
        fontName="Helvetica",
        textColor=_DARK,
        leading=14,
        leftIndent=14,
        bulletIndent=4,
        spaceAfter=2,
    )
    s_objective = ParagraphStyle(
        "objective",
        fontSize=9.5,
        fontName="Helvetica-Oblique",
        textColor=_DARK,
        leading=14,
        spaceAfter=4,
    )

    def divider():
        return HRFlowable(width="100%", thickness=1, color=_LIGHT_BLUE, spaceAfter=4, spaceBefore=2)

    def section_heading(text: str):
        return Paragraph(f"◈  {text.upper()}", s_section)

    # ── Content assembly ─────────────────────────────────────────────────────
    story = []

    # Header
    story.append(Paragraph(name or "Your Name", s_name))
    contact_parts = [p for p in [email, phone, location] if p]
    story.append(Paragraph("  |  ".join(contact_parts), s_contact))
    story.append(Spacer(1, 4))
    story.append(divider())

    # Career objective
    story.append(section_heading("Career Objective"))
    description = career_details.get("description", f"Aspiring {career} professional.")
    edu_list   = career_details.get("education", [])
    edu_str    = edu_list[0] if edu_list else stream
    objective  = (
        f"Motivated {stream} student seeking a challenging role as a {career}. "
        f"Pursuing {edu_str}. Committed to continuous learning and making a meaningful "
        f"contribution through strong technical and interpersonal skills."
    )
    story.append(Paragraph(objective, s_objective))

    # Education
    story.append(section_heading("Education"))
    edu_data = [[
        Paragraph("<b>Degree / Programme</b>", s_body),
        Paragraph("<b>Status</b>", s_body),
    ]]
    for edu in edu_list[:4]:
        edu_data.append([
            Paragraph(edu, s_body),
            Paragraph("Pursuing / Completed", s_body),
        ])
    if not edu_list:
        edu_data.append([Paragraph(f"{stream} stream — 12th Standard", s_body), Paragraph("Completed", s_body)])

    edu_table = Table(edu_data, colWidths=[4.2 * inch, 2.5 * inch])
    edu_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _LIGHT_BLUE),
        ("TEXTCOLOR",  (0, 0), (-1, 0), _WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_WHITE, _LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(edu_table)

    # Skills
    story.append(section_heading("Technical & Soft Skills"))
    skills: list[str] = career_details.get("skills", [])
    if extra_skills:
        skills = skills + [s.strip() for s in extra_skills.split(",") if s.strip()]
    if skills:
        skill_text = "  •  ".join(skills[:12])
        story.append(Paragraph(skill_text, s_body))

    # Career Roadmap as Experience
    story.append(section_heading("Career Roadmap & Milestones"))
    roadmap: list[str] = career_details.get("roadmap", [])
    for step in roadmap[:6]:
        story.append(Paragraph(f"• {step}", s_bullet))

    # Projects / Internships placeholder
    story.append(section_heading("Projects & Internship Experience"))
    projects = [
        f"Research Project on {career} — in-progress during academic year",
        f"Internship / Volunteer work related to {career_details.get('education', [stream])[0]}",
    ]
    for p in projects:
        story.append(Paragraph(f"• {p}", s_bullet))

    # Achievements
    story.append(section_heading("Achievements & Certifications"))
    ach_items = [a.strip() for a in achievements.split("\n") if a.strip()] if achievements else []
    if not ach_items:
        ach_items = [
            "Academic performance — consistent merit-list standing",
            "Active participation in school / college technical events",
            "Self-study certifications (online courses — Coursera/NPTEL)",
        ]
    for item in ach_items[:5]:
        story.append(Paragraph(f"• {item}", s_bullet))

    # Salary / Market at a glance
    story.append(section_heading("Career at a Glance"))
    salary = career_details.get("salary", "Competitive — varies by experience")
    market = career_details.get("market", "Growing sector with strong opportunities")
    story.append(Paragraph(f"<b>Expected Salary:</b>  {salary}", s_body))
    story.append(Paragraph(f"<b>Market Outlook:</b>  {market}", s_body))

    # Footer divider
    story.append(Spacer(1, 10))
    story.append(divider())
    story.append(Paragraph(
        f"Prepared using CareerGuidanceAI — {career} Career Path",
        ParagraphStyle("footer", fontSize=8, textColor=_GREY, alignment=TA_CENTER),
    ))

    doc.build(story)
    return buf.getvalue()
