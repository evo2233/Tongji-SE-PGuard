import argparse
from ultralytics import YOLO
import sys

# 确保标准输出和标准错误使用 UTF-8 编码
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Potato Defect Detection")
    parser.add_argument('--image_path', type=str, required=True, help="Path to the image to be processed")
    args = parser.parse_args()
    image_path=args.image_path
    model = YOLO("Potato.pt")  # 替换为你的模型路径
    results = model.predict(image_path)

    result = results[0]
    boxes=result.boxes

    cls = boxes.cls[0]# 类别索引
    conf = boxes.conf[0]  #


    print(f"类别: {cls}, 置信度: {conf:.2f}")

if __name__ == "__main__":
    main()