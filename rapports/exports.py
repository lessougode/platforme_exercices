"""Generation des fichiers Excel et PDF : liste d'etudiants et bulletins."""
from django.http import HttpResponse

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

ENTETE_COULEUR_XLSX = "1C2B45"       # openpyxl : hex sans #
ENTETE_COULEUR_PDF = "#1C2B45"       # reportlab : hex avec #


# ============================================================
# Liste d'etudiants (sans notes)
# ============================================================

def _lignes_etudiants(queryset):
    lignes = []
    for u in queryset.select_related('profil'):
        profil = getattr(u, 'profil', None)
        lignes.append([
            u.last_name or '-',
            u.first_name or '-',
            u.username,
            profil.get_role_display() if profil else '-',
            str(profil.groupe) if profil and profil.groupe else '-',
            profil.classe if profil else '-',
            u.email or '-',
            profil.numero_telephone if profil else '-',
        ])
    return lignes


def exporter_etudiants_excel(queryset):
    entetes = ['Nom', 'Prenom', 'Identifiant', 'Role', 'Groupe', 'Classe', 'Email', 'Telephone']
    lignes = _lignes_etudiants(queryset)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Etudiants"
    ws.append(entetes)
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=ENTETE_COULEUR_XLSX)
    for ligne in lignes:
        ws.append(ligne)
    for col in ws.columns:
        largeur = max(len(str(c.value)) for c in col if c.value) + 2
        ws.column_dimensions[col[0].column_letter].width = min(largeur, 40)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="etudiants.xlsx"'
    wb.save(response)
    return response


def exporter_etudiants_pdf(queryset):
    entetes = ['Nom', 'Prenom', 'Identifiant', 'Role', 'Groupe', 'Classe', 'Email']
    lignes = [l[:7] for l in _lignes_etudiants(queryset)]

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="etudiants.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(A4), topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Liste des etudiants", styles['Title']), Spacer(1, 12)]

    table = Table([entetes] + lignes, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(ENTETE_COULEUR_PDF)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f2ea")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(table)
    doc.build(elements)
    return response


# ============================================================
# Bulletin (notes + coefficients + moyenne + rang)
# ============================================================

def exporter_bulletin_excel(periode, groupe, evaluations, lignes):
    entetes = ['Rang', 'Nom', 'Prenom', 'Groupe']
    for ev in evaluations:
        entetes.append(f"{ev['label']} (coef {ev['coefficient']})")
    entetes += ['Moyenne /20', 'Moyenne /10']

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bulletin"
    titre = f"Bulletin - {periode.nom}" + (f" - {groupe.nom}" if groupe else "")
    ws.append([titre])
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(entetes))
    ws['A1'].font = Font(bold=True, size=14)
    ws.append([])
    ws.append(entetes)
    for cell in ws[3]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=ENTETE_COULEUR_XLSX)
        cell.alignment = Alignment(wrap_text=True)

    for ligne in lignes:
        profil = getattr(ligne['etudiant'], 'profil', None)
        row = [
            ligne['rang'] if ligne['rang'] is not None else '-',
            ligne['etudiant'].last_name or '-',
            ligne['etudiant'].first_name or '-',
            str(profil.groupe) if profil and profil.groupe else '-',
        ]
        for note in ligne['notes']:
            row.append(round(float(note), 2) if note is not None else '-')
        row.append(float(ligne['moyenne_20']) if ligne['moyenne_20'] is not None else '-')
        row.append(float(ligne['moyenne_10']) if ligne['moyenne_10'] is not None else '-')
        ws.append(row)

    from openpyxl.utils import get_column_letter
    for idx in range(1, len(entetes) + 1):
        lettre = get_column_letter(idx)
        valeurs = [str(ws.cell(row=r, column=idx).value) for r in range(3, ws.max_row + 1) if ws.cell(row=r, column=idx).value not in (None, '')]
        if valeurs:
            ws.column_dimensions[lettre].width = min(max(len(v) for v in valeurs) + 2, 30)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="bulletin.xlsx"'
    wb.save(response)
    return response


def exporter_bulletin_pdf(periode, groupe, evaluations, lignes):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bulletin.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(A4), topMargin=1.2*cm, bottomMargin=1.2*cm)
    styles = getSampleStyleSheet()
    titre = f"Bulletin - {periode.nom}" + (f" - {groupe.nom}" if groupe else " - Tous groupes")
    elements = [Paragraph(titre, styles['Title']), Spacer(1, 10)]

    entetes = ['Rang', 'Nom', 'Prenom'] + [f"{ev['label']}\n(coef {ev['coefficient']})" for ev in evaluations] + ['Moy. /20', 'Moy. /10']
    data = [entetes]
    for ligne in lignes:
        row = [
            str(ligne['rang']) if ligne['rang'] is not None else '-',
            ligne['etudiant'].last_name or '-',
            ligne['etudiant'].first_name or '-',
        ]
        for note in ligne['notes']:
            row.append(f"{note:.2f}" if note is not None else '-')
        row.append(f"{ligne['moyenne_20']:.2f}" if ligne['moyenne_20'] is not None else '-')
        row.append(f"{ligne['moyenne_10']:.2f}" if ligne['moyenne_10'] is not None else '-')
        data.append(row)

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(ENTETE_COULEUR_PDF)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f2ea")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)
    doc.build(elements)
    return response
