"""
UMDAC Datathon 2026 — Editable PowerPoint (.pptx) Builder for Dashboards & Insights
Team: Plot Twists
Outputs:
  1. dashboards.pptx (10 widescreen slides: native editable rule/header textboxes + 4 individual movable chart PNGs per slide)
  2. insights.pptx   (12 widescreen slides: native editable Cover Page, 10 Feature Group slides with editable rule/economy/methodology boxes + movable charts, and editable Master Causal DAG slide)
"""
import sys
import os
import zipfile
from xml.sax.saxutils import escape
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

import build_dashboard as bd

CHART_DIR = os.path.join(BASE_DIR, "agg", "pptx_charts")
os.makedirs(CHART_DIR, exist_ok=True)

# 16:9 Widescreen dimensions in inches (13.333 x 7.5) -> EMUs (1 inch = 914400 EMUs)
SLIDE_W_IN = 13.333333
SLIDE_H_IN = 7.5
EMU = 914400

def to_emu(val_norm, total_in):
    return int(round(val_norm * total_in * EMU))


# ==============================================================================
# PURE-PYTHON OPENXML (.PPTX) WRITER (100% Native Editable Shapes & Pictures)
# ==============================================================================
class PptxBuilder:
    def __init__(self):
        self.slides = []
        self.media = {}  # filename -> bytes

    def add_slide(self):
        s = {"shapes": [], "pics": []}
        self.slides.append(s)
        return s

    def add_rect(self, slide, x, y, w, h, fill_hex=None, line_hex=None, line_pt=1.0, rounded=False):
        slide["shapes"].append({
            "type": "rect",
            "x": to_emu(x, SLIDE_W_IN),
            "y": to_emu(y, SLIDE_H_IN),
            "w": to_emu(w, SLIDE_W_IN),
            "h": to_emu(h, SLIDE_H_IN),
            "fill": fill_hex.lstrip("#").upper() if fill_hex else None,
            "line": line_hex.lstrip("#").upper() if line_hex else None,
            "line_w": int(round(line_pt * 12700)),
            "prst": "roundRect" if rounded else "rect",
            "paragraphs": [],
            "anchor": "t",
        })

    def add_textbox(self, slide, x, y, w, h, paragraphs, fill_hex=None, line_hex=None, line_pt=1.0, rounded=False, anchor="t", margin_in=0.08):
        """
        paragraphs: list of dicts or tuples:
          {"text": str, "size": float(pt), "color": "#hex", "bold": bool, "italic": bool, "align": "l"|"ctr"|"r", "space_after": float(pt)}
        """
        slide["shapes"].append({
            "type": "textbox",
            "x": to_emu(x, SLIDE_W_IN),
            "y": to_emu(y, SLIDE_H_IN),
            "w": to_emu(w, SLIDE_W_IN),
            "h": to_emu(h, SLIDE_H_IN),
            "fill": fill_hex.lstrip("#").upper() if fill_hex else None,
            "line": line_hex.lstrip("#").upper() if line_hex else None,
            "line_w": int(round(line_pt * 12700)),
            "prst": "roundRect" if rounded else "rect",
            "paragraphs": paragraphs,
            "anchor": anchor,
            "margin": int(round(margin_in * EMU)),
        })

    def add_picture(self, slide, img_path, x, y, w, h):
        fname = os.path.basename(img_path)
        if fname not in self.media:
            with open(img_path, "rb") as f:
                self.media[fname] = f.read()
        slide["pics"].append({
            "fname": fname,
            "x": to_emu(x, SLIDE_W_IN),
            "y": to_emu(y, SLIDE_H_IN),
            "w": to_emu(w, SLIDE_W_IN),
            "h": to_emu(h, SLIDE_H_IN),
        })

    def save(self, out_path):
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
            # 1. [Content_Types].xml
            ct_overrides = [
                '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
                '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
                '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
                '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
            ]
            for i in range(1, len(self.slides) + 1):
                ct_overrides.append(
                    f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
                )
            ct_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Default Extension="png" ContentType="image/png"/>'
                + "".join(ct_overrides)
                + "</Types>"
            )
            z.writestr("[Content_Types].xml", ct_xml)

            # 2. _rels/.rels
            rels_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
                '</Relationships>'
            )
            z.writestr("_rels/.rels", rels_xml)

            # 3. ppt/presentation.xml & ppt/_rels/presentation.xml.rels
            sld_ids = []
            pres_rels = [
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>',
                '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>',
            ]
            for i in range(1, len(self.slides) + 1):
                rid = f"rId{i + 2}"
                sld_ids.append(f'<p:sldId id="{255 + i}" r:id="{rid}"/>')
                pres_rels.append(
                    f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
                )

            pres_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
                '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
                f'<p:sldIdLst>{"".join(sld_ids)}</p:sldIdLst>'
                f'<p:sldSz cx="{int(SLIDE_W_IN * EMU)}" cy="{int(SLIDE_H_IN * EMU)}"/>'
                f'<p:notesSz cx="{int(SLIDE_H_IN * EMU)}" cy="{int(SLIDE_W_IN * EMU)}"/>'
                '<p:defaultTextStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:defaultTextStyle>'
                '</p:presentation>'
            )
            z.writestr("ppt/presentation.xml", pres_xml)
            z.writestr(
                "ppt/_rels/presentation.xml.rels",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                + "".join(pres_rels)
                + "</Relationships>",
            )

            # 4. Slide Master, Slide Layout & Theme
            sm_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
                '<p:cSld><p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/></p:bgRef></p:bg>'
                '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
                '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
                '</p:spTree></p:cSld>'
                '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
                '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>'
                '</p:sldMaster>'
            )
            z.writestr("ppt/slideMasters/slideMaster1.xml", sm_xml)
            z.writestr(
                "ppt/slideMasters/_rels/slideMaster1.xml.rels",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
                '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>'
                '</Relationships>',
            )

            sl_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">'
                '<p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
                '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
                '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
            )
            z.writestr("ppt/slideLayouts/slideLayout1.xml", sl_xml)
            z.writestr(
                "ppt/slideLayouts/_rels/slideLayout1.xml.rels",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>'
                '</Relationships>',
            )

            theme_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">'
                '<a:themeElements>'
                '<a:clrScheme name="Office">'
                '<a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1>'
                '<a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1>'
                '<a:dk2><a:srgbClr val="1F4E79"/></a:dk2>'
                '<a:lt2><a:srgbClr val="EEF3F8"/></a:lt2>'
                '<a:accent1><a:srgbClr val="1F4E79"/></a:accent1>'
                '<a:accent2><a:srgbClr val="E07B39"/></a:accent2>'
                '<a:accent3><a:srgbClr val="2A9D8F"/></a:accent3>'
                '<a:accent4><a:srgbClr val="C0392B"/></a:accent4>'
                '<a:accent5><a:srgbClr val="8E6BBF"/></a:accent5>'
                '<a:accent6><a:srgbClr val="7F8C8D"/></a:accent6>'
                '<a:hlink><a:srgbClr val="0563C1"/></a:hlink>'
                '<a:folHlink><a:srgbClr val="954F72"/></a:folHlink>'
                '</a:clrScheme>'
                '<a:fontScheme name="Office">'
                '<a:majorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>'
                '<a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>'
                '</a:fontScheme>'
                '<a:fmtScheme name="Office">'
                '<a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>'
                '<a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="25400"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="38100"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>'
                '<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>'
                '<a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>'
                '</a:fmtScheme>'
                '</a:themeElements></a:theme>'
            )
            z.writestr("ppt/theme/theme1.xml", theme_xml)

            # 5. Write media files
            for fname, bdata in self.media.items():
                z.writestr(f"ppt/media/{fname}", bdata)

            # 6. Write each slide XML & rels
            for idx, s in enumerate(self.slides, 1):
                s_rels = [
                    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
                ]
                sp_elements = []
                obj_id = 2

                for sh in s["shapes"]:
                    fill_xml = f'<a:solidFill><a:srgbClr val="{sh["fill"]}"/></a:solidFill>' if sh["fill"] else "<a:noFill/>"
                    line_xml = (
                        f'<a:ln w="{sh["line_w"]}"><a:solidFill><a:srgbClr val="{sh["line"]}"/></a:solidFill></a:ln>'
                        if sh["line"]
                        else '<a:ln><a:noFill/></a:ln>'
                    )
                    m_val = sh.get("margin", 68580)
                    anchor = sh.get("anchor", "t")
                    tx_paras = []
                    for p in sh["paragraphs"]:
                        align = p.get("align", "l")
                        spc_a = int(round(p.get("space_after", 3.0) * 100))
                        sz = int(round(p.get("size", 11.0) * 100))
                        b_attr = ' b="1"' if p.get("bold") else ""
                        i_attr = ' i="1"' if p.get("italic") else ""
                        col_hex = p.get("color", "#1C2833").lstrip("#").upper()
                        font_face = p.get("font", "Calibri")
                        lines = str(p.get("text", "")).split("\n")
                        for l_i, line_str in enumerate(lines):
                            cur_spc = spc_a if l_i == len(lines) - 1 else 100
                            tx_paras.append(
                                f'<a:p><a:pPr algn="{align}"><a:lnSpc><a:spcPct val="118000"/></a:lnSpc>'
                                f'<a:spcAft><a:spcPts val="{cur_spc}"/></a:spcAft></a:pPr>'
                                f'<a:r><a:rPr lang="en-US" sz="{sz}"{b_attr}{i_attr} dirty="0">'
                                f'<a:solidFill><a:srgbClr val="{col_hex}"/></a:solidFill>'
                                f'<a:latin typeface="{font_face}"/></a:rPr>'
                                f'<a:t>{escape(line_str)}</a:t></a:r></a:p>'
                            )
                    if not tx_paras:
                        tx_paras.append('<a:p><a:endParaRPr lang="en-US"/></a:p>')

                    sp_xml = (
                        f'<p:sp>'
                        f'<p:nvSpPr><p:cNvPr id="{obj_id}" name="Shape {obj_id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                        f'<p:spPr><a:xfrm><a:off x="{sh["x"]}" y="{sh["y"]}"/><a:ext cx="{sh["w"]}" cy="{sh["h"]}"/></a:xfrm>'
                        f'<a:prstGeom prst="{sh["prst"]}"><a:avLst/></a:prstGeom>{fill_xml}{line_xml}</p:spPr>'
                        f'<p:txBody><a:bodyPr wrap="square" lIns="{m_val}" tIns="{m_val}" rIns="{m_val}" bIns="{m_val}" anchor="{anchor}"/>'
                        f'<a:lstStyle/>{"".join(tx_paras)}</p:txBody>'
                        f'</p:sp>'
                    )
                    sp_elements.append(sp_xml)
                    obj_id += 1

                for p_idx, pic in enumerate(s["pics"], 2):
                    rid = f"rId{p_idx}"
                    s_rels.append(
                        f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{pic["fname"]}"/>'
                    )
                    pic_xml = (
                        f'<p:pic>'
                        f'<p:nvPicPr><p:cNvPr id="{obj_id}" name="Chart {obj_id}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
                        f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
                        f'<p:spPr><a:xfrm><a:off x="{pic["x"]}" y="{pic["y"]}"/><a:ext cx="{pic["w"]}" cy="{pic["h"]}"/></a:xfrm>'
                        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
                        f'</p:pic>'
                    )
                    sp_elements.append(pic_xml)
                    obj_id += 1

                slide_xml = (
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
                    '<p:cSld><p:spTree>'
                    '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
                    '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
                    + "".join(sp_elements)
                    + "</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>"
                )
                z.writestr(f"ppt/slides/slide{idx}.xml", slide_xml)
                z.writestr(
                    f"ppt/slides/_rels/slide{idx}.xml.rels",
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    + "".join(s_rels)
                    + "</Relationships>",
                )


# ==============================================================================
# STEP 1: RENDER INDIVIDUAL PANEL CHARTS FOR DASHBOARDS.PPTX & INSIGHTS.PPTX
# ==============================================================================
def save_single_panel_charts():
    """Renders each of the 4 panels of Dashboards 1..10 as standalone high-res PNGs."""
    panel_paths = {}
    for idx, (title, fn) in enumerate(bd.PAGES, 1):
        # First render the 4 axes on separate figures by creating 4 single-axis figures
        figs_axes = []
        for p_i in range(4):
            f = plt.figure(figsize=(6.4, 3.1), dpi=180, facecolor="white")
            ax = f.add_subplot(111)
            figs_axes.append((f, ax))
        fn([fa[1] for fa in figs_axes])
        panel_paths[idx] = []
        for p_i, (f, _) in enumerate(figs_axes, 1):
            p_path = os.path.join(CHART_DIR, f"dash_{idx:02d}_p{p_i}.png")
            try:
                f.tight_layout(pad=0.6)
            except Exception:
                pass
            f.savefig(p_path, dpi=180, bbox_inches="tight", pad_inches=0.08)
            plt.close(f)
            panel_paths[idx].append(p_path)
    return panel_paths


# ==============================================================================
# STEP 2: BUILD DASHBOARDS.PPTX (10 Editable Widescreen Slides)
# ==============================================================================
def build_dashboards_pptx(panel_paths):
    pptx = PptxBuilder()
    for idx, (title, _) in enumerate(bd.PAGES, 1):
        s = pptx.add_slide()
        # Top Header Banner (Native Editable Shape)
        pptx.add_textbox(
            s, 0.0, 0.0, 1.0, 0.065,
            [{"text": f"Feature Group {title}", "size": 16, "color": "#FFFFFF", "bold": True}],
            fill_hex="#1F4E79", anchor="ctr", margin_in=0.18
        )
        pptx.add_textbox(
            s, 0.55, 0.0, 0.43, 0.065,
            [{"text": f"UMDAC Datathon 2026  ·  Team: Plot Twists  ·  Dashboard {idx} / 10", "size": 10.5, "color": "#CBD5E1", "align": "r"}],
            anchor="ctr", margin_in=0.10
        )

        # Reconstructed Causal Business Rules Box (Native Editable Rounded Box)
        pptx.add_textbox(
            s, 0.025, 0.080, 0.95, 0.145,
            [
                {"text": "RECONSTRUCTED CAUSAL BUSINESS RULES (N = 10,000,000):", "size": 9.5, "color": "#1F4E79", "bold": True, "space_after": 2},
                {"text": bd.RULES[title], "size": 9.0, "color": "#0F172A", "space_after": 0},
            ],
            fill_hex="#EEF3F8", line_hex="#1F4E79", line_pt=1.2, rounded=True, margin_in=0.08
        )

        # 4 Individual Movable Chart Panels (2x2 Grid)
        coords = [
            (0.025, 0.240, 0.465, 0.350),
            (0.510, 0.240, 0.465, 0.350),
            (0.025, 0.605, 0.465, 0.350),
            (0.510, 0.605, 0.465, 0.350),
        ]
        for p_path, (cx, cy, cw, ch) in zip(panel_paths[idx], coords):
            pptx.add_picture(s, p_path, cx, cy, cw, ch)

        # Editable Footer
        pptx.add_textbox(
            s, 0.025, 0.962, 0.75, 0.035,
            [{"text": "UMDAC Datathon 2026 — Swift Payments Case Study (Team: Plot Twists). Full population n = 10,000,000.", "size": 8.0, "color": "#64748B"}],
            margin_in=0.02
        )
        pptx.add_textbox(
            s, 0.85, 0.962, 0.125, 0.035,
            [{"text": f"Page {idx} of 10", "size": 8.0, "color": "#64748B", "align": "r"}],
            margin_in=0.02
        )

    out_file = os.path.join(BASE_DIR, "dashboards.pptx")
    pptx.save(out_file)
    print("Wrote ->", out_file)


# ==============================================================================
# STEP 3: BUILD INSIGHTS.PPTX (12 Editable Widescreen Slides)
# ==============================================================================
SLIDE_DATA = [
    {
        "section": "Feature group 1  ·  Data quality and scale",
        "headline": "Complete 10M-row synthetic book, 6 anomaly classes, and an end-of-month surge",
        "rules": (
            "1. Hidden Row-0 Blueprint: Row 0 contains an undocumented 21st column (DISCLAIMER) stating the book was generated exclusively via hard-coded rules, NumPy random draws, and Python Faker.\n"
            "2. Population Integrity: Across all 10,000,000 retained rows (30 Apr 2023 11:22 UTC to 31 Jul 2023 09:56 UTC), timestamp, USD amount, BIC path, and party details have 0.00% nulls, USD_AMOUNT > 0 everywhere, and exact row duplicates are 1 in 10M.\n"
            "3. Anomaly Rarity & Monthly Surge: ANOMALY_TYPE is populated on 7,006 rows (0.0701%) across 6 classes (including undocumented CUSTOMER_RECALL, n=317). Daily volume surges +55% across Days 19–30 (peaking on Day 26 at 4.91%)."
        ),
        "econ": (
            "A live monitoring team can treat the dataset as a clean, complete ledger without broken records or missing mandatory MT103 fields. "
            "Any fraud/error detector must operate at a 1-in-1,427 base rate (0.070%) while accommodating a 55% end-of-month corporate payroll and accounts-payable settlement surge during the final 12 days of each month."
        ),
        "method": (
            "Out-of-core full-population scan inspected raw CSV headers/row 0 (uncovering the 21st DISCLAIMER column), verified exact null rates, distinct row hashes, and positivity constraints across all 10,000,000 records, and decomposed daily volume into weekly and day-of-month (1..31) components."
        ),
        "charts": (1, 1, 3),  # dashboard 1, panels B (index 1) and D (index 3)
        "ref": "Supporting charts: dashboards.pdf, Page 1.",
    },
    {
        "section": "Feature group 2  ·  Time patterns",
        "headline": "Every country follows one universal 24-hour curve in the sender's local timezone",
        "rules": (
            "1. Universal Local-Time Circadian Law: Shifting UTC hour by the Ordering Country's UTC offset (H_local = (H_UTC + TZ_OFFSET(ORD_COUNTRY)) mod 24) collapses all countries onto ONE identical 24-hour curve: nighttime trough 01:00–06:00 (~0.95%/hr), morning opening spike at 08:00 local (7.60%), and lunch dip at 12:00 (4.25%).\n"
            "2. Party-Specific Evening Peak: Businesses ('B') peak at 17:00–19:00 local (7.6%, treasury cutoff), whereas Consumers ('C') peak 2 hours later at 19:00 local (8.2%, evening retail banking).\n"
            "3. Weekly Cycle & Flat Anomaly Rate: Mon–Fri carry 88.82% of volume (1.70M–1.83M/day) vs Sat (0.435M) and Sun (0.684M). Anomaly rate is invariant across UTC hours (0.056%–0.089%)."
        ),
        "econ": (
            "Domestic RTGS clearing systems (Fedwire, TARGET2, CHAPS, CNAPS) open around 08:00 local time and enforce corporate treasury cutoffs at 17:00–18:00 local time, while retail consumers submit remittances after work (~19:00 local). "
            "Because anomaly injection is independent of timestamp, off-hours screening provides zero fraud lift over daytime screening."
        ),
        "method": (
            "Computed UTC hourly distributions per Ordering Country (CN peak 00:00/08:00 UTC, DE/FR/CH 06:00/15:00–17:00 UTC, GB 07:00/18:00 UTC, US 12:00/23:00 UTC) and aligned each by its May–July 2023 UTC offset (+8, +2, +1, -4), proving exact curve invariance across jurisdictions."
        ),
        "charts": (2, 0, 1),
        "ref": "Supporting charts: dashboards.pdf, Page 2.",
    },
    {
        "section": "Feature group 3  ·  Currency",
        "headline": "Path-weighted currency selection (20:1 sender weight) and the 100% FX hop identity",
        "rules": (
            "1. Path-Weighted Currency Selection (20:1 Weight on B_0): On 98.77% of complete paths, CURRENCY_CODE is drawn from the native currencies of the banks in BIC8_PATH, with Ordering Bank B_0 weighted ~20:1 against each subsequent bank B_1..B_{K-1} (95.6% B_0 at K=2; 92.1% B_0 at K=3). Only 1.23% use an offshore vehicle currency.\n"
            "2. Home Currency Dominance: Consequently, 86%–95% of payments use the sender's domestic currency (DE 94.5% EUR, FR 94.0% EUR, US 90.5% USD, CH 88.8% CHF, GB 88.6% GBP, SG 87.5% SGD, CN 86.2% CNY).\n"
            "3. 100.000% Exact FX Conversion Identity: CURRENCY_CONVERSION_COUNT = sum_{i=1}^{K-1} I(NativeCurr(B_i) != NativeCurr(B_{i+1})) with 0 errors across 30,000 continuous paths — explaining why 36.9% of domestic-endpoint payments convert currency when routed via foreign intermediaries."
        ),
        "econ": (
            "Senders overwhelmingly denominate payment instructions in their local funding currency, leaving cross-currency conversion to correspondent banks along the route. "
            "Even when sender and beneficiary reside in the same country, routing through an international clearing hub (e.g., USD or EUR cover bank) triggers two back-to-back FX conversions along the chain."
        ),
        "method": (
            "Conditioned CURRENCY_CODE on complete paths where all K banks have distinct native currencies to isolate the exact 20:1 selection weights, and tested the adjacent country-currency transition sum against CURRENCY_CONVERSION_COUNT (100.000% match)."
        ),
        "charts": (3, 1, 2),
        "ref": "Supporting charts: dashboards.pdf, Page 3.",
    },
    {
        "section": "Feature group 4  ·  Payment value",
        "headline": "Exact +2.0 natural-log step per Business party, GDP scaling, and 38.7% round amounts",
        "rules": (
            "1. Exact +2.0 Natural-Log Party-Type Law: ln(USD_AMOUNT) ~ Normal(mu_pair + delta_GDP(ORD_COUNTRY), sigma_ln^2) with constant sigma_log10 = 1.00, where mu_ln steps up by EXACTLY +2.0 (e^2 = 7.39x in USD) per Business ('B') participant: C->C mu_ln = 6.00 (med USD 463) | B->C & C->B mu_ln = 8.00 (med USD 3,119 / USD 3,229) | B->B mu_ln = 10.00 (med USD 22,888).\n"
            "2. Ordering Country GDP-per-Capita Scaling: Mean log10(USD) scales linearly with Ordering Country GDP per capita (SD = 0.457 across sender countries: MC 4.43, LU 3.97, US 3.77 vs IN 2.38, VN 2.35) and has ZERO causal dependence on Beneficiary Country (SD = 0.056).\n"
            "3. 38.69% Round Local-Currency Rule & Daily FX Table: 38.69% of payments are generated as exact round denominations (100, 500, 1k, 5k, 10k, 100k) in local CURRENCY_CODE and multiplied by a daily exchange rate FX(currency, date)."
        ),
        "econ": (
            "Retail peer-to-peer remittances (~USD 463), commercial salary/invoice payouts (~USD 3,150), and wholesale B2B trade settlements (~USD 22,888) sit separated by uniform multiplicative steps (e^2 = 7.39x). "
            "Transaction sizes scale with the macroeconomic purchasing power (GDP per capita) of the originating economy, while human contract conventions produce sharp clusters at round local-currency denominations."
        ),
        "method": (
            "Performed two-way fixed-effects variance decomposition across (ORD_COUNTRY × BEN_COUNTRY × Party_Pair), proving an 8.2x dispersion ratio between Sender Country (SD=0.457) and Receiver Country (SD=0.056), and extracted daily FX rates from same-day USD_AMOUNT ratios."
        ),
        "charts": (4, 0, 1),
        "ref": "Supporting charts: dashboards.pdf, Page 4.",
    },
    {
        "section": "Feature group 5  ·  Routing and corridors",
        "headline": "BIC8 sequential indexing, Zipf hub scaling, and 100% home vs 99% offshore banking",
        "rules": (
            "1. BIC8 Naming Rule ('BBBBCCLO'): Characters 0..3 (BBBB) are a 0-indexed sequential bank ID within country CC (0000..1135 for 1,136 US banks; 0000..0677 for 678 GB banks; 0000..0636 for 637 DE banks), char 6 (L) is the city code ('3'=NY, '2'=London), and char 7 is '0'.\n"
            "2. Zipf Hub Concentration: Across 26,764 corridors, country volume scales as a power law of its bank pool size. US->US is the largest corridor (385,598 rows, 3.86%); top 15 corridors capture 16.1%; top bank pair 0001MQM0->0009TNT0 repeats 20,005 times.\n"
            "3. 100% Home Ordering vs 99% Offshore Beneficiary Pool: Ordering parties bank 100.0% in their residential country (ORD_BIC8[4:6] == ORD_TOKENS country), whereas Beneficiary BICs are drawn independently across the global bank pool (0.98% address match; domestic bank share = P(BEN_C = c): 24.3% in US, <10% elsewhere)."
        ),
        "econ": (
            "Senders initiate wires from their domestic relationship bank (100% home match), whereas multinational beneficiaries, exporters, and treasury centers receive funds across global settlement hubs (especially the United States, Switzerland, and Britain). "
            "Because US banks represent ~24% of the beneficiary pool, ~24% of US-originated wires settle domestically inside the US while smaller countries settle >90% cross-border."
        ),
        "method": (
            "Parsed all 8,392 ORDERING_BIC8 and 8,266 BENEFICIARY_BIC8 strings to verify 0..N-1 sequential indexing per country, regressed log country volume on log bank count, and cross-tabulated <country_code:XX> tokens against BIC8[4:6]."
        ),
        "charts": (5, 1, 2),
        "ref": "Supporting charts: dashboards.pdf, Page 5.",
    },
    {
        "section": "Feature group 6  ·  Path structure",
        "headline": "Euler (1/e) geometric hop decay, constant 88.7/11.3 split, and 5% per-hop dropout",
        "rules": (
            "1. Shifted Geometric Hop Decay with Exact Euler Ratio (1/e = 0.3679): Observable bank count K = PARTICIPANT_COUNT (K >= 2) follows P(K = k) = (1 - 1/e)*(1/e)^(k-2): observed P(K=2) = 63.2328% vs theoretical 1 - 1/e = 63.2121%, with constant step decay ratio P(K+1)/P(K) = 0.3676 across all K.\n"
            "2. Deterministic & Constant Product Split: K == 2 maps 100.0% to 'Direct' (6,323,280 rows). Every K >= 3 splits at an invariant ratio of 88.69% 'Indirect' (3,260,758 rows) vs 11.31% 'Covered' (415,962 rows).\n"
            "3. The 5.0% Per-Hop Dropout Law: Each hop along the path drops out of visibility with p = 5.0%: internal drops insert '...' and set CONTINUITY_QFLAG = 'N' (767,204 rows, 7.672%, 0 disagreements), while boundary drops create unflagged 5.0% endpoint mismatches (BIC8_PATH[:8] != ORD_BIC8 in 4.99%, BIC8_PATH[-8:] != BEN_BIC8 in 4.95% where QFLAG stays 'Y'!)."
        ),
        "econ": (
            "When two banks lack a direct bilateral account (36.77% of wires), they route either serially through intermediary banks (Indirect MT103 chain, 88.7%) or via a separate reimbursement cover path (Covered MT103 + MT202 COV, 11.3%). "
            "Non-reporting intermediary hops create internal tracker gaps ('...', QFLAG='N'), whereas an unreported first or last leg truncates the path endpoint without triggering an internal gap flag."
        ),
        "method": (
            "Regressed log P(PARTICIPANT_COUNT = K) on K (recovering exact natural-log slope -1.000 => 1/e), verified 100% equivalence between '...' and QFLAG='N', and tested endpoint equality BIC8_PATH[:8]==ORD_BIC8 and BIC8_PATH[-8:]==BEN_BIC8."
        ),
        "charts": (6, 0, 3),
        "ref": "Supporting charts: dashboards.pdf, Page 6.",
    },
    {
        "section": "Feature group 7  ·  Duration",
        "headline": "The R² = 0.9982 Directed-Edge Additive Latency Law and the 45x cover speedup",
        "rules": (
            "1. Bimodal Directed-Edge Latency Matrix L(B_i -> B_{i+1}): Every ordered bank pair has a fixed intrinsic latency L(B_i -> B_{i+1}) (within-edge SD ~ 6.8s) drawn from two regimes: ~73% Fast STP edges (9.5s–25s; Direct median = 39s) vs ~27% Slow Manual/Batch edges (100s–8,215s).\n"
            "2. Exact Multi-Hop Additive Latency Law (R² = 0.998212): For any complete path [B_1, B_2, ..., B_K], total duration is strictly the sum of its directed edge latencies minus a constant 17.0s endpoint overhead per intermediary: TOTAL_DURATION = sum_{i=1}^{K-1} L(B_i -> B_{i+1}) - 17.0*(K - 2) + eps.\n"
            "3. Chain Length vs Cover Speedup Paradox: Across the whole book, median duration rises with K (39s at K=2, 126s at K=3, 418s at K=4, 2,171s at K=12; Indirect med 281s, Covered 383s; Gap '...' med 155s vs Continuous 54s). Yet for a slow direct edge (0219US30->0159US30, 424.1s), routing via two fast cover STP edges settles in 9.4s (45x faster)!"
        ),
        "econ": (
            "In live correspondent banking, bilateral links without automated STP or pre-funded liquidity require manual repair or batch queuing (~20+ minutes). "
            "Routing through a major clearing intermediary replaces one slow bilateral link with two automated STP hops, settling in under 10 seconds."
        ),
        "method": (
            "Estimated mean edge latency L(B_i -> B_j) exclusively from 2-bank Direct paths, then predicted 3-bank path duration out-of-sample as L(B1->B2) + L(B2->B3) - 17.0s across 7,395 paths, achieving R² = 0.998212."
        ),
        "charts": (7, 1, 2),
        "ref": "Supporting charts: dashboards.pdf, Page 7.",
    },
    {
        "section": "Feature group 8  ·  Party types",
        "headline": "Independent Bernoulli counterparty sampling (78.8% B × 28.8% B) and e² value steps",
        "rules": (
            "1. Strict Statistical Independence of Party Types: ORDERING_TYPE ~ Bernoulli(p_B = 78.75%) and BENEFICIARY_TYPE ~ Bernoulli(p_B = 28.82%) are drawn independently (Chi-square p = 0.89; joint counts match P(Ord)*P(Ben) to within 0.01% across 10M rows):\n"
            "   • B -> C: 5,603,692 rows (56.04% obs vs 56.05% theo), median USD 3,119\n"
            "   • B -> B: 2,270,945 rows (22.71% obs vs 22.70% theo), median USD 22,888\n"
            "   • C -> C: 1,514,758 rows (15.15% obs vs 15.13% theo), median USD 463\n"
            "   • C -> B:   610,605 rows ( 6.11% obs vs  6.12% theo), median USD 3,229\n"
            "2. Product & Corridor Invariance: Business sender share is identical across Direct, Indirect, and Covered routing (78.8% B) and stays within 75%–86% across all major countries."
        ),
        "econ": (
            "Corporates ('B') originate nearly four-fifths of payment instructions (global payroll, supplier invoices, benefits, and wholesale trade), while individuals ('C') are the majority recipients (71.2%) because B2C payroll/disbursements (56.0% of the book) outnumber B2B invoices (22.7%) by 2.5 to 1. "
            "Each Business participant multiplies the median payment value by e^2 = 7.39x (USD 463 -> USD 3,150 -> USD 22,888)."
        ),
        "method": (
            "Constructed the full 2×2 contingency table on all 10,000,000 rows, tested independence against the product of marginals P(Ord_B)=0.78746 and P(Ben_B)=0.28815, and checked conditional invariance across TRANSACTION_TYPE_CODE and ORD_COUNTRY."
        ),
        "charts": (8, 0, 1),
        "ref": "Supporting charts: dashboards.pdf, Page 8.",
    },
    {
        "section": "Feature group 9  ·  Party details and accounts",
        "headline": "The 6-digit PARTY_ID cipher, 100% B/C token exclusivity, and MT103 field templates",
        "rules": (
            "1. The 6-Digit PARTY_ID Cipher: Every underlying person/company has a permanent 6-digit PARTY_ID = re.sub('\\D','',account)[-6:] embedded at the end of their _FAKE_ account across all banks (e.g., IBAN '_FAKE_<CC><check><BankID>00000000<PARTY_ID>' on 91%–96% of European wires vs 0% in US/SG/CN/HK/JP/AU).\n"
            "2. Heavy-Tailed Account Reuse: Across 391,132 ordering accounts, 33% send once, median is 3, max is 75,803, and the top 1% originate 46% of all payments. Across 2.59M beneficiary accounts, 78% receive a single payment.\n"
            "3. 100% Token Exclusivity & 3 MT103 Templates: <business:N> (85.5%) and <company_keyword:N> (26.5%) occur 100.0% in 'B'; <first_name:N> (57.8%) and <last_name:N> (86.1%) occur 100.0% in 'C'. Details follow 83.3% MT103 50K (<line_break:35> wrap), 15.0% 50F ('1/ 2/ 3/'), 1.4% 50A, plus 9.3% '//' prefix."
        ),
        "econ": (
            "In live SWIFT FIN MT103 traffic, Field 50K/59 enforces a legacy 4×35-character line wrap (<line_break:35>), Field 50F uses structured '1/ 2/ 3/' subfields, and European banks mandate ISO 13616 IBANs while US/APAC rails use domestic BBANs. "
            "De-anonymizing the 6-digit PARTY_ID resolves multi-bank entities across all 2.59 million beneficiary accounts."
        ),
        "method": (
            "Grouped identical BENEFICIARY_DETAILS across distinct BENEFICIARY_BIC8 banks to uncover the invariant 6-digit tail cipher and 4-digit bank prefix, and cross-tabulated all <tag:N> tokens against ORDERING_TYPE and BENEFICIARY_TYPE."
        ),
        "charts": (9, 1, 3),
        "ref": "Supporting charts: dashboards.pdf, Page 9.",
    },
    {
        "section": "Feature group 10  ·  Anomaly labels",
        "headline": "Five generative anomaly rules, a shared 1,068-mule pool, and a grounded negative proof",
        "rules": (
            "1. Shared 1,068-Mule Syndicate Pool (Romance, CEO & Account Replacement): Decoding our 6-digit PARTY_ID cipher proves all 3 fraud classes route into ONE shared pool of 1,068 mule beneficiary IDs (378 Romance, 634 CEO, 462 Acc.Rep; overlaps |R∩C|=136, |C∩A|=225, |R∩A|=99) in slow offshore banks (mean duration 1,159s–1,558s vs 563s normal; 0.0% last-hop truncation!).\n"
            "   • ROMANCE_SCAM (2,476): 100% C sender; 500 victims each send N ~ U[2..8] escalating wires (med USD 109) with identical details & path.\n"
            "   • CEO_SCAM (945): 100% B sender (72.3% B->C) where B->C amounts are hijacked to the B->B corporate scale (med USD 20,602 vs USD 3,119 normal B->C!).\n"
            "   • ACCOUNT_REPLACEMENT_SCAM (649): Normal party/amount wire whose BENEFICIARY_ACCOUNT is swapped to a mule PARTY_ID in the 1,068 pool.\n"
            "2. Operational Errors & Grounded Negative Result: FAT_FINGER (1,940) shifts decimal by ×10^k (med 71x sender norm, sigma=2.25); DUPLICATE (679) clones 185 wires U[2..5]x (med gap 410s); undocumented CUSTOMER_RECALL (317) is a pure uniform random label (all KS p in [0.22, 0.87])."
        ),
        "econ": (
            "Organized laundering syndicates reuse the same offshore money-mule accounts across romance grooming, BEC/CEO executive spoofing, and vendor invoice redirection. "
            "Meanwhile, CUSTOMER_RECALL (SWIFT camt.056) reflects a sender's post-initiation cancellation request (e.g., commercial dispute), so the original MT103 wire is statistically identical to normal traffic."
        ),
        "method": (
            "Decoded 6-digit BEN_PID across all 7,006 anomalies to prove the 1,068-mule intersection, conditioned CEO_SCAM on B->C pairs to expose the 7x scale hijack, and ran formal Two-Sample KS tests on CUSTOMER_RECALL vs normal traffic."
        ),
        "charts": (10, 1, 3),
        "ref": "Supporting charts: dashboards.pdf, Page 10.",
    },
]


def build_insights_pptx(panel_paths):
    pptx = PptxBuilder()

    # ------------------------------------------------------------------
    # SLIDE 1: DEDICATED COVER PAGE (All Native Editable Shapes!)
    # ------------------------------------------------------------------
    s1 = pptx.add_slide()
    pptx.add_rect(s1, 0.0, 0.0, 1.0, 1.0, fill_hex="#1F4E79")
    pptx.add_rect(s1, 0.0, 0.0, 1.0, 0.08, fill_hex="#133352")
    pptx.add_textbox(
        s1, 0.04, 0.015, 0.75, 0.05,
        [{"text": "UNIVERSITI MALAYA DATA ANALYTICS COMPETITION  ·  PRELIMINARY ROUND", "size": 11, "color": "#93C5FD", "bold": True}],
        anchor="ctr", margin_in=0.02
    )
    pptx.add_textbox(
        s1, 0.85, 0.015, 0.11, 0.05,
        [{"text": "1  /  12", "size": 10, "color": "#93C5FD", "align": "r"}],
        anchor="ctr", margin_in=0.02
    )
    pptx.add_textbox(
        s1, 0.04, 0.11, 0.64, 0.18,
        [
            {"text": "UMDAC Datathon 2026", "size": 20, "color": "#E07B39", "bold": True, "space_after": 4},
            {"text": "Reverse-Engineering the Synthetic Swift Payment Book:\nCausal Business Rules, Latent Ciphers & Economic Mechanics", "size": 19, "color": "#FFFFFF", "bold": True},
        ],
        margin_in=0.02
    )
    # Group Badge Box
    pptx.add_textbox(
        s1, 0.70, 0.12, 0.26, 0.13,
        [
            {"text": "SUBMITTED BY GROUP", "size": 9, "color": "#93C5FD", "bold": True, "align": "ctr", "space_after": 3},
            {"text": "Plot Twists", "size": 19, "color": "#FFFFFF", "bold": True, "align": "ctr"},
        ],
        fill_hex="#133352", line_hex="#E07B39", line_pt=1.8, anchor="ctr", margin_in=0.05
    )
    pptx.add_rect(s1, 0.04, 0.30, 0.92, 0.005, fill_hex="#E07B39")
    pptx.add_textbox(
        s1, 0.04, 0.32, 0.92, 0.12,
        [{
            "text": (
                "Complete structural reverse-engineering of 10,000,000 fictitious cross-border payments across 20 features.\n"
                "Pages 2–11 present the reconstructed business rules, supporting charts, live-market economic behaviour, and causal methodology "
                "for each of the 10 feature groups (matching dashboards.pdf Pages 1–10), followed by the Master Causal Graph on Page 12."
            ),
            "size": 10.5, "color": "#E2E8F0"
        }],
        margin_in=0.02
    )

    cards_left = [
        ("Slide 2  ·  Group 1: Data Quality & Scale", "Row-0 DISCLAIMER, 0% nulls, 6 anomaly classes & Days 19–30 payroll surge"),
        ("Slide 3  ·  Group 2: Time Patterns", "Universal 24h sender local-time curve, B (17:00) vs C (19:00) peaks & 88.8% weekday share"),
        ("Slide 4  ·  Group 3: Currency", "Path-weighted currency selection (20:1 B_0 weight) & 100.000% exact FX conversion identity"),
        ("Slide 5  ·  Group 4: Payment Value", "Exact +2.0 ln(USD) step per 'B' party, Sender GDP scaling & 38.69% local round rule"),
        ("Slide 6  ·  Group 5: Routing & Corridors", "BIC8 'BBBBCCLO' indexing, Zipf scaling & 100% Home Ordering vs 99% Global Beneficiary pool"),
    ]
    cards_right = [
        ("Slide 7  ·  Group 6: Path Structure", "Euler 1/e (0.3679) geometric hop decay, 88.7/11.3 split & 5.0%/hop '...' / boundary dropout"),
        ("Slide 8  ·  Group 7: Duration", "Directed-Edge Additive Latency Law (R² = 0.9982), bimodal corridors & 45x cover speedup"),
        ("Slide 9  ·  Group 8: Party Types", "Independent Bernoulli sampling (78.75% B Ord × 28.82% B Ben) & product/country invariance"),
        ("Slide 10 ·  Group 9: Accounts & Tokens", "6-digit PARTY_ID tail cipher, 100% B/C token exclusivity & MT103 50K/50F/50A templates"),
        ("Slide 11 ·  Group 10: Anomaly Labels", "Shared 1,068-mule syndicate pool, Fat-Finger ×10^k, 185 Dupes & CUSTOMER_RECALL KS null proof"),
    ]
    for i, (ct, cs) in enumerate(cards_left):
        pptx.add_textbox(
            s1, 0.04, 0.46 + i * 0.088, 0.44, 0.076,
            [
                {"text": ct, "size": 10, "color": "#E07B39", "bold": True, "space_after": 1},
                {"text": cs, "size": 8.5, "color": "#CBD5E1"},
            ],
            fill_hex="#163A5F", line_hex="#335C85", line_pt=0.8, anchor="ctr", margin_in=0.05
        )
    for i, (ct, cs) in enumerate(cards_right):
        pptx.add_textbox(
            s1, 0.52, 0.46 + i * 0.088, 0.44, 0.076,
            [
                {"text": ct, "size": 10, "color": "#38BDF8", "bold": True, "space_after": 1},
                {"text": cs, "size": 8.5, "color": "#CBD5E1"},
            ],
            fill_hex="#163A5F", line_hex="#335C85", line_pt=0.8, anchor="ctr", margin_in=0.05
        )
    pptx.add_textbox(
        s1, 0.04, 0.915, 0.92, 0.05,
        [{"text": "Slide 12  ·  Master Causal DAG, Operational Screening Blueprint & Analytical Limits", "size": 10, "color": "#93C5FD", "bold": True}],
        margin_in=0.02
    )

    # ------------------------------------------------------------------
    # SLIDES 2–11: FEATURE GROUPS 1–10 (1 Slide per Feature Group)
    # ------------------------------------------------------------------
    for s_idx, item in enumerate(SLIDE_DATA, 2):
        s = pptx.add_slide()
        # Top Header Bar
        pptx.add_textbox(
            s, 0.0, 0.0, 1.0, 0.055,
            [{"text": item["section"], "size": 10.5, "color": "#FFFFFF", "bold": True}],
            fill_hex="#1F4E79", anchor="ctr", margin_in=0.15
        )
        pptx.add_textbox(
            s, 0.55, 0.0, 0.42, 0.055,
            [{"text": "UMDAC Datathon 2026  ·  Team: Plot Twists", "size": 10.5, "color": "#FFFFFF", "align": "r"}],
            anchor="ctr", margin_in=0.08
        )
        # Slide Title
        pptx.add_textbox(
            s, 0.035, 0.072, 0.93, 0.065,
            [{"text": item["headline"], "size": 17, "color": "#1F4E79", "bold": True}],
            margin_in=0.02
        )
        # Left Box 1: Reconstructed Causal Business Rules
        pptx.add_textbox(
            s, 0.035, 0.145, 0.49, 0.39,
            [
                {"text": "RECONSTRUCTED CAUSAL BUSINESS RULES", "size": 8.5, "color": "#1F4E79", "bold": True, "space_after": 3},
                {"text": item["rules"], "size": 9.3, "color": "#1C2833", "space_after": 2},
            ],
            fill_hex="#EEF3F8", line_hex="#1F4E79", line_pt=1.0, margin_in=0.08
        )
        # Left Box 2: Real-World Economic & Live-System Behaviour
        pptx.add_textbox(
            s, 0.035, 0.555, 0.49, 0.21,
            [
                {"text": "REAL-WORLD ECONOMIC & LIVE-SYSTEM BEHAVIOUR", "size": 8.5, "color": "#2A9D8F", "bold": True, "space_after": 3},
                {"text": item["econ"], "size": 9.3, "color": "#1C2833"},
            ],
            margin_in=0.04
        )
        # Left Box 3: Methodology & Causal Identification
        pptx.add_textbox(
            s, 0.035, 0.775, 0.49, 0.17,
            [
                {"text": "METHODOLOGY & CAUSAL IDENTIFICATION", "size": 8.5, "color": "#E07B39", "bold": True, "space_after": 3},
                {"text": item["method"], "size": 9.0, "color": "#5D6D7E"},
            ],
            margin_in=0.04
        )
        # Right Column: Two Movable Supporting Charts
        d_no, c1_idx, c2_idx = item["charts"]
        pptx.add_picture(s, panel_paths[d_no][c1_idx], 0.545, 0.145, 0.425, 0.375)
        pptx.add_picture(s, panel_paths[d_no][c2_idx], 0.545, 0.535, 0.425, 0.375)

        # Reference & Page Number (No population footer!)
        pptx.add_textbox(
            s, 0.55, 0.925, 0.32, 0.04,
            [{"text": item["ref"], "size": 8.5, "color": "#5D6D7E", "italic": True}],
            margin_in=0.02
        )
        pptx.add_textbox(
            s, 0.88, 0.945, 0.09, 0.04,
            [{"text": f"{s_idx}  /  12", "size": 9.0, "color": "#5D6D7E", "align": "r"}],
            margin_in=0.02
        )

    # ------------------------------------------------------------------
    # SLIDE 12: MASTER CAUSAL SYNTHESIS & SCREENING BLUEPRINT (All Editable!)
    # ------------------------------------------------------------------
    s12 = pptx.add_slide()
    pptx.add_textbox(
        s12, 0.0, 0.0, 1.0, 0.055,
        [{"text": "Master Causal Synthesis  ·  Methodology & Screening Blueprint", "size": 10.5, "color": "#FFFFFF", "bold": True}],
        fill_hex="#1F4E79", anchor="ctr", margin_in=0.15
    )
    pptx.add_textbox(
        s12, 0.55, 0.0, 0.42, 0.055,
        [{"text": "UMDAC Datathon 2026  ·  Team: Plot Twists", "size": 10.5, "color": "#FFFFFF", "align": "r"}],
        anchor="ctr", margin_in=0.08
    )
    pptx.add_textbox(
        s12, 0.035, 0.072, 0.93, 0.065,
        [{"text": "End-to-end structural causal architecture and live-system screening rules", "size": 17, "color": "#1F4E79", "bold": True}],
        margin_in=0.02
    )

    # Left Container for 7-Stage Causal DAG (Each DAG node is an editable shape!)
    pptx.add_textbox(
        s12, 0.035, 0.145, 0.48, 0.80,
        [{"text": "RECONSTRUCTED 7-STAGE GENERATIVE CAUSAL GRAPH (SCM)", "size": 9.5, "color": "#1F4E79", "bold": True, "align": "ctr"}],
        fill_hex="#F8FAFC", line_hex="#CBD5E1", line_pt=1.0, margin_in=0.06
    )
    dag_nodes = [
        (0.050, 0.200, 0.215, 0.155, "#DBEAFE", "#1F4E79", "1. EXOGENOUS WORLD GRAPH", "• Country Zipf Weights, GDP/cap, TZ\n• 8,392 BIC8s ('BBBBCCLO' 0..N-1)\n• Directed Edge Latencies L(B_i→B_j)"),
        (0.285, 0.200, 0.215, 0.155, "#DBEAFE", "#1F4E79", "2. PARTY REGISTRY (FAKER)", "• Permanent 6-Digit PARTY_ID Cipher\n• Indep. P(Ord=B)=78.8%, P(Ben=B)=28.8%\n• 100% Home Ord vs 99% Global Ben"),
        (0.050, 0.375, 0.215, 0.155, "#DCFCE7", "#2A9D8F", "3. TEMPORAL & FX CLOCK", "• Universal 24h Local Curve + TZ Shift\n• 88.8% Weekday + Days 19–30 Surge\n• 92-Day Latent FX(currency, date)"),
        (0.285, 0.375, 0.215, 0.155, "#DCFCE7", "#2A9D8F", "4. ROUTING & LATENCY ENGINE", "• Hops K ~ ShiftedGeom(1/e = 0.3679)\n• 5%/Hop Dropout ('...' & Boundary)\n• Exact FX Count; D = Σ L_e - 17(K-2)"),
        (0.050, 0.550, 0.215, 0.165, "#F3E8FF", "#8E6BBF", "5. AMOUNT & CURRENCY ENGINE", "• μ_ln = 6 + 2·I(Ord=B) + 2·I(Ben=B)\n• + Sender Country GDP/Capita Scaling\n• 38.7% Round Local × FX(c, date)\n• Path Currency (20:1 B_0 Weight)"),
        (0.285, 0.550, 0.215, 0.165, "#FEF3C7", "#E07B39", "6. MT103 TEXT & TOKENIZER", "• 83.3% 50K (<line_break:35> wrap)\n• 15.0% 50F ('1/2/3/'), 1.4% 50A\n• 100% B vs C Token Exclusivity\n• 9.3% '//' Prefix; 5.9% No Account"),
        (0.050, 0.735, 0.450, 0.190, "#FEE2E2", "#C0392B", "7. POST-GENERATION ANOMALY INTERVENTIONS (7,006 ROWS / 0.0701%)",
         "• Shared 1,068-Mule Pool (Slow Banks, 0% Last Drop): Romance (500×U[2..8] bursts),\n  CEO Scam (100% B; B→C hijacked to B→B scale), Account Replacement (redirected to mule ID)\n• Operational: Fat Finger (×10^k shift, σ=2.25), Duplicate (185 clusters × U[2..5], med 410s)\n• Grounded Negative Result: CUSTOMER_RECALL (317 rows) = Uniform Random Label (KS p > 0.22)"),
    ]
    for (nx, ny, nw, nh, nbg, nec, ntitle, nbody) in dag_nodes:
        pptx.add_textbox(
            s12, nx, ny, nw, nh,
            [
                {"text": ntitle, "size": 8.0, "color": nec, "bold": True, "space_after": 2},
                {"text": nbody, "size": 7.6, "color": "#1C2833"},
            ],
            fill_hex=nbg, line_hex=nec, line_pt=1.2, rounded=True, margin_in=0.05
        )

    # Right Column: 5 Editable Operational Screening Blocks
    screening_blocks = [
        ("1. Entity Resolution via 6-Digit PARTY_ID Cipher (CEO & Acct. Replacement)",
         "Screening raw BENEFICIARY_ACCOUNT misses multi-bank syndicates. Extracting PARTY_ID = digits(account)[-6:] links 2.59M accounts and exposes the 1,068 shared mule entities across Romance, CEO, and Account Replacement scams."),
        ("2. Context-Conditional Amount Screening (Fat Finger & CEO B->C Hijacking)",
         "Flag payments >10x–50x the sender's historical median (catching Fat Finger ×10^k shifts) and B->C payments at B->B scale (~USD 20.6k vs USD 3.1k norm, catching CEO Scam)."),
        ("3. Short-Window Deduping & Burst Tracking (Duplicate & Romance Scams)",
         "Flag identical (Ord_Acc, Ben_Acc, Amount, Currency) instructions within 20 minutes (med 410s for the 185 Duplicate clusters vs 15 days for normal repeats) and rapid Consumer bursts (N in 2..8) to offshore accounts."),
        ("4. Value of Grounded Negative Results (CUSTOMER_RECALL & Flat UTC Clock)",
         "Formal KS tests (p in 0.22–0.87) prove CUSTOMER_RECALL (317 rows) has zero feature distortion at initiation, and hourly anomaly rates are flat (0.056%–0.089%). Knowing what NOT to weight prevents false positives."),
        ("5. Full-Population Verification Discipline",
         "Every count, percentage, median, and identity across Dashboards 1–10 and Slides 2–12 is verified on all 10,000,000 rows alongside explicit causal conditioning."),
    ]
    for i, (stitle, sbody) in enumerate(screening_blocks):
        pptx.add_textbox(
            s12, 0.535, 0.145 + i * 0.160, 0.435, 0.148,
            [
                {"text": stitle, "size": 9.5, "color": "#1F4E79", "bold": True, "space_after": 2},
                {"text": sbody, "size": 8.8, "color": "#1C2833"},
            ],
            fill_hex="#F8FAFC", line_hex="#CBD5E1", line_pt=0.8, rounded=True, margin_in=0.06
        )

    pptx.add_textbox(
        s12, 0.88, 0.945, 0.09, 0.04,
        [{"text": "12  /  12", "size": 9.0, "color": "#5D6D7E", "align": "r"}],
        margin_in=0.02
    )

    out_file = os.path.join(BASE_DIR, "insights.pptx")
    pptx.save(out_file)
    print("Wrote ->", out_file)


if __name__ == "__main__":
    print("Rendering 40 individual high-resolution chart panels...", flush=True)
    panels = save_single_panel_charts()
    print("Building editable dashboards.pptx...", flush=True)
    build_dashboards_pptx(panels)
    print("Building editable insights.pptx...", flush=True)
    build_insights_pptx(panels)
    print("All done!")
