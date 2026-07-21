---
name: a5-card-stand-generator
description: A5 카드 스탠드용 인포그래픽 이미지 조절 및 A4 300DPI 2단 출력용 합판(절취선 포함) 이미지 생성 가이드 및 스크립트
---

# A5 카드 스탠드 인포그래픽 출력 파일 생성 스킬 (A5 Card Stand Generator)

본 스킬은 9:16 비율 또는 원본 인포그래픽 이미지들을 A5 카드 스탠드에 출력 가능한 형태로 맞춤 변형(1748x2480px, 시계방향 90도 회전하여 2480x1748px)한 뒤, A4 300DPI (2480x3508px) 해상도의 캔버스에 위/아래 2개씩 배치하고 중앙 절취선을 추가하여 출력용 PNG 파일(`출력용1.png`, `출력용2.png` 등)을 생성하는 규격 및 수순을 정의합니다.

## 핵심 규격 및 절차 (Workflow & Specifications)

1. **개별 이미지 비율 및 규격 조정 (A5 카드 규격)**:
   - 목표 단일 카드 해상도: `1748 x 2480 px` (A5 @ 300DPI)
   - 원본 이미지 비율을 유지하면서 `1748 x 2480 px` 캔버스 중앙에 패딩(여백)과 함께 배치.
   - 필요 시 여백 조정 (예: 특정 이미지 콘텐츠를 좌/우로 offset 이동).

2. **90도 시계방향 회전 (가로 배치용)**:
   - A5 카드를 시계 방향(오른쪽)으로 90도 회전시켜 `2480 x 1748 px` 해상도로 변환.

3. **A4 300DPI 2단 배치 및 절취선 생성 (2480 x 3508 px)**:
   - A4 세로 캔버스 (`2480 x 3508 px`, 300DPI 메타데이터 지정) 생성.
   - 상단(Y: 0 ~ 1754px 영역 중앙) 및 하단(Y: 1754 ~ 3508px 영역 중앙)에 각각 회전된 이미지 배치.
   - 중앙 경계선(Y = 1754px)에 파선(Dashed Cut Line, Gray `(100, 100, 100)`) 생성.
   - `출력용1.png`, `출력용2.png` 등 300DPI PNG 파일로 최종 저장.

## Python 파이프라인 참고 코드

```python
import os
from PIL import Image, ImageDraw

def generate_a5_card_stand_sheets(image_pairs, docs_dir='docs', output_prefix='출력용'):
    canvas_w, canvas_h = 2480, 3508 # A4 @ 300DPI
    half_h = canvas_h // 2 # 1754
    
    for i, (top_path, bot_path) in enumerate(image_pairs, start=1):
        canvas = Image.new('RGBA', (canvas_w, canvas_h), (255, 255, 255, 255))
        
        top_img = Image.open(top_path)
        bot_img = Image.open(bot_path)
        
        top_x = (canvas_w - top_img.width) // 2
        top_y = (half_h - top_img.height) // 2
        
        bot_x = (canvas_w - bot_img.width) // 2
        bot_y = half_h + (half_h - bot_img.height) // 2
        
        canvas.paste(top_img, (top_x, top_y), top_img if top_img.mode == 'RGBA' else None)
        canvas.paste(bot_img, (bot_x, bot_y), bot_img if bot_img.mode == 'RGBA' else None)
        
        # 가운데 절취선
        draw = ImageDraw.Draw(canvas)
        dash_len, gap_len = 30, 20
        line_color = (100, 100, 100, 255)
        line_width = 4
        
        x = 20
        while x < canvas_w - 20:
            x_end = min(x + dash_len, canvas_w - 20)
            draw.line([(x, half_h), (x_end, half_h)], fill=line_color, width=line_width)
            x += dash_len + gap_len
            
        out_filename = f"{output_prefix}{i}.png"
        out_path = os.path.join(docs_dir, out_filename)
        canvas.save(out_path, dpi=(300, 300))
        print(f"Saved: {out_path}")
```
