from PIL import Image
import os

def create_tileset():
    # 타일 이미지 경로 (사용자가 제공한 순서대로)
    tile_images = [
        '../Resources/tile/TileSet_0.png',  # 0
        '../Resources/tile/TileSet_1.png',  # 1
        '../Resources/tile/TileSet_2.png',  # 2
    ]

    # 첫 번째 이미지를 열어서 타일 크기 확인
    first_img = Image.open(tile_images[0])
    tile_width, tile_height = first_img.size

    # 4열 x 3행 타일셋 생성
    cols, rows = 1,3
    tileset_width = tile_width * cols
    tileset_height = tile_height * rows

    # 새 이미지 생성 (RGBA 모드)
    tileset = Image.new('RGBA', (tileset_width, tileset_height))

    # 각 타일을 타일셋에 배치
    for idx, tile_path in enumerate(tile_images):
        if idx >= cols * rows:  # 12개까지만
            break

        row = idx // cols
        col = idx % cols

        tile_img = Image.open(tile_path)
        x = col * tile_width
        y = row * tile_height

        tileset.paste(tile_img, (x, y))
        print(f"타일 {idx + 1} 배치 완료: ({col}, {row}) at ({x}, {y})")

    # 저장
    output_path = '../Resources/tile/combined_tiles.png'
    tileset.save(output_path)
    print(f"\n타일셋 생성 완료: {output_path}")
    print(f"크기: {tileset_width}x{tileset_height} (타일 크기: {tile_width}x{tile_height})")

if __name__ == '__main__':
    create_tileset()

