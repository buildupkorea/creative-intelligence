"""
Image Extractor — Excel 파일에서 소재 이미지를 자동 추출
"""

import zipfile
import base64
import xml.etree.ElementTree as ET
from io import BytesIO


def extract_images(uploaded_file):
    """Extract images from Excel file and map to creative positions"""
    images = {}
    
    try:
        file_bytes = BytesIO(uploaded_file.read())
        uploaded_file.seek(0)
        
        with zipfile.ZipFile(file_bytes, 'r') as zf:
            # Find all media files
            media_files = [f for f in zf.namelist() if f.startswith('xl/media/')]
            
            # Find drawing relationships to map images to positions
            drawing_rels = {}
            for f in zf.namelist():
                if f.startswith('xl/drawings/_rels/') and f.endswith('.rels'):
                    tree = ET.parse(BytesIO(zf.read(f)))
                    root = tree.getroot()
                    ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
                    for rel in root.findall('.//r:Relationship', {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}):
                        # Handle default namespace
                        pass
                    # Parse without namespace
                    for rel in root.iter():
                        if 'Relationship' in rel.tag:
                            rid = rel.get('Id', '')
                            target = rel.get('Target', '')
                            if 'image' in target.lower():
                                drawing_name = f.split('/')[-1].replace('.rels', '')
                                if drawing_name not in drawing_rels:
                                    drawing_rels[drawing_name] = {}
                                drawing_rels[drawing_name][rid] = target.replace('../media/', '')
            
            # Extract image positions from drawing XML files
            image_positions = {}
            for f in zf.namelist():
                if f.startswith('xl/drawings/drawing') and f.endswith('.xml') and '_rels' not in f:
                    drawing_name = f.split('/')[-1]
                    rels = drawing_rels.get(drawing_name.replace('.xml', '.xml'), {})
                    
                    tree = ET.parse(BytesIO(zf.read(f)))
                    root = tree.getroot()
                    
                    # Define namespaces
                    ns = {
                        'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
                        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
                    }
                    
                    for anchor in root.findall('.//xdr:twoCellAnchor', ns):
                        fr = anchor.find('xdr:from', ns)
                        if fr is not None:
                            col = int(fr.find('xdr:col', ns).text)
                            row = int(fr.find('xdr:row', ns).text)
                        
                        pic = anchor.find('.//xdr:pic', ns)
                        if pic is not None:
                            blip = pic.find('.//a:blip', ns)
                            if blip is not None:
                                embed = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                                if embed and embed in rels:
                                    img_file = rels[embed]
                                    image_positions[f"r{row}_c{col}"] = img_file
            
            # Read all image files as base64
            for media_file in media_files:
                img_name = media_file.split('/')[-1]
                img_data = zf.read(media_file)
                ext = 'jpeg' if img_name.endswith(('.jpeg', '.jpg')) else 'png'
                b64 = base64.b64encode(img_data).decode()
                images[img_name] = {
                    'b64': b64,
                    'ext': ext,
                    'size': len(img_data)
                }
    
    except Exception as e:
        print(f"Image extraction error: {e}")
    
    return images


def get_creative_images(images, creative_positions=None):
    """
    Map extracted images to creative names.
    Returns dict of {creative_name: base64_string}
    """
    result = {}
    
    # Sort images by size to distinguish thumbnails from full-size
    sorted_imgs = sorted(images.items(), key=lambda x: x[1]['size'])
    
    # Small images (< 100KB) are likely thumbnails in Summary/Creative sheets
    thumbnails = [(k, v) for k, v in sorted_imgs if v['size'] < 100000]
    
    for i, (name, data) in enumerate(thumbnails):
        result[f"creative_{i}"] = data['b64']
    
    return result
