"""
Excel Parser — 캠페인 리포트 엑셀을 자동 파싱
센카/UNO 등 다양한 형식 지원
"""

import pandas as pd
import openpyxl
from io import BytesIO


def parse_excel(uploaded_file):
    """Parse campaign report Excel file"""
    wb = openpyxl.load_workbook(BytesIO(uploaded_file.read()), data_only=True)
    uploaded_file.seek(0)  # Reset for image extraction
    
    result = {
        'client': '',
        'campaign': '',
        'period': '',
        'budget': 0,
        'creatives': [],
        'media': [],
        'daily': [],
    }
    
    # ===== Parse Summary Sheet =====
    if 'Summary' in wb.sheetnames:
        ws = wb['Summary']
        result['client'] = str(ws['C2'].value or '')
        result['campaign'] = str(ws['C3'].value or '')
        result['period'] = str(ws['C4'].value or '')
        result['budget'] = float(ws['C5'].value or 0)
    
    # ===== Parse Creative Sheet =====
    if 'Creative' in wb.sheetnames:
        ws = wb['Creative']
        result['creatives'] = parse_creative_sheet(ws)
    
    # ===== Parse Media Data from Summary =====
    if 'Summary' in wb.sheetnames:
        result['media'] = parse_media_from_summary(wb['Summary'])
    
    # ===== Parse Daily Sheet =====
    if 'Daily' in wb.sheetnames:
        result['daily'] = parse_daily_sheet(wb['Daily'])
    
    wb.close()
    return result


def parse_creative_sheet(ws):
    """Parse the Creative sheet for ad performance data"""
    creatives = []
    
    # Find the META(전환) section - usually starts around row 24
    header_row = None
    for row in range(1, ws.max_row + 1):
        cell_b = ws.cell(row, 2).value
        cell_c = ws.cell(row, 3).value
        if cell_b == 'MEDIA' and cell_c == '시안':
            header_row = row
            break
    
    if not header_row:
        # Try alternate format
        for row in range(1, ws.max_row + 1):
            if ws.cell(row, 6).value == 'Imps' and ws.cell(row, 7).value == 'Clicks':
                header_row = row
                break
    
    if not header_row:
        return creatives
    
    # Parse rows after header
    current_media = ''
    current_product = ''
    
    for row in range(header_row + 1, ws.max_row + 1):
        b_val = ws.cell(row, 2).value
        c_val = ws.cell(row, 3).value
        d_val = ws.cell(row, 4).value
        f_val = ws.cell(row, 6).value  # Imps
        
        # Check for media label
        if b_val and 'META' in str(b_val):
            current_media = str(b_val)
        if b_val and ('TOTAL' in str(b_val) or 'Grand' in str(b_val)):
            continue
        
        # Check for product label
        if c_val and not d_val:
            current_product = str(c_val)
            continue
        if c_val and d_val:
            current_product = str(c_val)
        
        # Parse creative data
        if d_val and f_val and isinstance(f_val, (int, float)) and f_val > 0:
            creative = {
                'media': current_media,
                'product': current_product,
                'name': str(d_val),
                'imps': float(f_val or 0),
                'clicks': float(ws.cell(row, 7).value or 0),
                'action': float(ws.cell(row, 8).value or 0),
                'rev': float(ws.cell(row, 9).value or 0),
                'cvr': float(ws.cell(row, 10).value or 0),
                'ctr': float(ws.cell(row, 11).value or 0),
                'cpm': float(ws.cell(row, 12).value or 0),
                'cpc': float(ws.cell(row, 13).value or 0),
                'cpa': float(ws.cell(row, 14).value or 0),
                'roas': float(ws.cell(row, 15).value or 0),
                'cost': float(ws.cell(row, 16).value or 0),
                'note': str(ws.cell(row, 17).value or ''),
            }
            
            # Handle #DIV/0! and other errors
            for key in ['cvr', 'ctr', 'cpm', 'cpc', 'cpa', 'roas']:
                if isinstance(creative[key], str) or creative[key] is None:
                    creative[key] = 0
            
            creatives.append(creative)
    
    return creatives


def parse_media_from_summary(ws):
    """Parse media-level data from Summary sheet"""
    media = []
    
    # Look for the TOTAL row (usually row 15)
    for row in range(10, min(40, ws.max_row + 1)):
        b_val = ws.cell(row, 2).value
        c_val = ws.cell(row, 3).value
        
        if b_val and 'META' in str(b_val) and c_val:
            m = {
                'name': f"{b_val} ({c_val})",
                'imps': float(ws.cell(row, 5).value or 0),
                'clicks': float(ws.cell(row, 8).value or 0),
                'action': float(ws.cell(row, 14).value or 0),
                'ctr': float(ws.cell(row, 17).value or 0),
                'cost': float(ws.cell(row, 19).value or 0),
                'cpc': 0,
            }
            if m['clicks'] > 0:
                m['cpc'] = m['cost'] / m['clicks']
            media.append(m)
    
    return media


def parse_daily_sheet(ws):
    """Parse daily data"""
    daily = []
    
    # Find the daily data rows (look for date values)
    for row in range(10, min(30, ws.max_row + 1)):
        b_val = ws.cell(row, 2).value
        d_val = ws.cell(row, 4).value  # Total imps
        
        if b_val and hasattr(b_val, 'strftime') and d_val and isinstance(d_val, (int, float)):
            daily.append({
                'date': b_val.strftime('%m/%d'),
                'day': str(ws.cell(row, 3).value or ''),
                'imps': float(d_val or 0),
                'clicks': float(ws.cell(row, 5).value or 0),
                'action': float(ws.cell(row, 6).value or 0),
                'cost': float(ws.cell(row, 11).value or 0),
            })
    
    return daily
