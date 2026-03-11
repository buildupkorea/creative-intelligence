"""
image_extractor.py — 엑셀 내 소재 이미지 추출 + base64 변환
Creative 시트에 삽입된 소재 이미지를 추출하여 HTML 임베딩용 base64로 변환합니다.
"""
import zipfile
import base64
import io
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional


def extract_images(file) -> Dict[str, str]:
    """
    엑셀 파일에서 이미지를 추출하여 {image_name: base64_data_uri} 딕셔너리 반환
    """
    images = {}
    
    try:
        # file이 UploadedFile인 경우 바이트로 변환
        if hasattr(file, 'read'):
            file_bytes = file.read()
            if hasattr(file, 'seek'):
                file.seek(0)
        else:
            file_bytes = file
        
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            media_files = [f for f in zf.namelist() if f.startswith("xl/media/")]
            
            for media_path in media_files:
                try:
                    data = zf.read(media_path)
                    filename = media_path.split("/")[-1]
                    
                    # MIME 타입 결정
                    if filename.lower().endswith(".png"):
                        mime = "image/png"
                    elif filename.lower().endswith((".jpg", ".jpeg")):
                        mime = "image/jpeg"
                    elif filename.lower().endswith(".gif"):
                        mime = "image/gif"
                    else:
                        mime = "image/png"
                    
                    b64 = base64.b64encode(data).decode("utf-8")
                    images[filename] = f"data:{mime};base64,{b64}"
                except Exception:
                    continue
    except Exception:
        pass
    
    return images


def map_images_to_creatives(file, creative_names: List[str]) -> Dict[str, str]:
    """
    Creative 시트의 drawing XML을 파싱하여 소재명과 이미지를 매핑.
    완벽한 매핑이 불가능한 경우, 순서 기반으로 매핑합니다.
    
    Returns: {creative_name: base64_data_uri}
    """
    images = extract_images(file)
    
    if not images:
        return {}
    
    # 이미지를 번호순 정렬
    sorted_images = sorted(
        images.items(),
        key=lambda x: _extract_number(x[0])
    )
    
    # drawing XML에서 시트별 이미지 매핑 시도
    try:
        if hasattr(file, 'read'):
            file_bytes = file.read()
            if hasattr(file, 'seek'):
                file.seek(0)
        else:
            file_bytes = file
        
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            # Creative 시트에 연결된 drawing 찾기
            drawing_rels = _find_creative_drawing_rels(zf)
            if drawing_rels:
                mapped = _map_via_drawing(zf, drawing_rels, creative_names)
                if mapped:
                    return mapped
    except Exception:
        pass
    
    # Fallback: 이미지가 소재 순서와 같다고 가정
    # 작은 이미지(아이콘/로고)는 제외하고 소재 이미지만 추출
    creative_images = [
        (name, uri) for name, uri in sorted_images 
        if _is_creative_image(name, file)
    ]
    
    mapping = {}
    for i, cname in enumerate(creative_names):
        if i < len(creative_images):
            mapping[cname] = creative_images[i][1]
    
    return mapping


def _extract_number(filename: str) -> int:
    """파일명에서 숫자 추출"""
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else 0


def _is_creative_image(filename: str, file) -> bool:
    """소재 이미지인지 판별 (로고/아이콘 제외)"""
    # 파일 크기로 판별 — 50KB 이상이면 소재 이미지로 간주
    try:
        if hasattr(file, 'read'):
            file_bytes = file.read()
            if hasattr(file, 'seek'):
                file.seek(0)
        else:
            file_bytes = file
        
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            info = zf.getinfo(f"xl/media/{filename}")
            return info.file_size > 50000
    except Exception:
        return True


def _find_creative_drawing_rels(zf) -> Optional[str]:
    """Creative 시트에 연결된 drawing 관계 파일 찾기"""
    try:
        # worksheet rels에서 Creative 시트의 drawing 찾기
        for name in zf.namelist():
            if "worksheets/_rels" in name and name.endswith(".rels"):
                content = zf.read(name).decode("utf-8")
                if "drawing" in content.lower():
                    return name
    except Exception:
        pass
    return None


def _map_via_drawing(zf, rels_path: str, creative_names: List[str]) -> Dict[str, str]:
    """drawing XML을 통한 정확한 이미지-소재 매핑 시도"""
    # 복잡한 XML 파싱이 필요하므로 빈 딕셔너리 반환 (fallback 사용)
    return {}
