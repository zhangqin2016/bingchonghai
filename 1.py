from ultralytics import YOLO


def main():
    # 加载自定义模型
    model = YOLO("best.pt")  # 使用自定义模型

    # 对图片进行目标检测
    results = model("image.jpg")  # 替换为你的图片路径

    # 检查结果是否为列表
    if isinstance(results, list):
        for result in results:
            result.show()  # 显示每个结果
    else:
        results.show()  # 如果不是列表，直接显示结果


if __name__ == "__main__":
    main()
帮忙把这个py