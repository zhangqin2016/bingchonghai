import io
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Dictionary to store models
models = {}

# Load a model and store it in the dictionary
def load_model(model_name):
    if model_name not in models:
        try:
            models[model_name] = YOLO(model_name)
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            return None
    return models[model_name]

# Encode image to Base64
def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# Decode Base64 to image
def decode_image(base64_string):
    img_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(img_data))
    return image

# Define a fixed color mapping for models
model_color_map = {
 'best.pt': '#FF0000',
'heibanbing_best.pt': '#00FF00',
'junhebing_best.pt': '#0000FF',
'shuangmeibing_best.pt':'#FFA500'
}

default_color = 'orange'  # Default color for models not in the map

def draw_boxes(image, boxes, confidences, classes, class_names, model_name, color, legend):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("test.ttf", 15)

    for i in range(len(boxes)):
        x1, y1, x2, y2 = boxes[i]
        conf = confidences[i]
        cls = int(classes[i])
        label = f"{class_names[cls]} {conf * 100:.1f}%"

        # Draw rectangle and text
        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
        text_bbox = draw.textbbox((x1, y1 - 10), label, font=font)
        text_size = (text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1])

        padding = 5
        draw.rectangle([x1, y1 - text_size[1] - padding, x1 + text_size[0], y1], fill=color)
        draw.text((x1, y1 - text_size[1] - padding), label, fill="white", font=font)

    # Update legend with model and color
    legend.append((model_name, color))

    return image

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    # Get model names from the request
    model_names = data.get('model_names', ['best.pt'])

    if 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400

    # Decode the input image
    base64_image = data['image']
    img = decode_image(base64_image)

    annotated_image = img.copy()

    # To store the legend info
    legend = []

    # To store the confidences for each model
    confidences_data = {}

    for model_name in model_names:
        model = load_model(model_name)
        if model is None:
            return jsonify({'error': f"Failed to load model {model_name}"}), 400

        # Perform prediction
        results = model(img)
        class_names = model.names
        boxes = results[0].boxes.xyxy.numpy()
        confidences = results[0].boxes.conf.numpy().tolist()
        classes = results[0].boxes.cls.numpy()

        # Use fixed color for the model, fallback to default if not specified
        color = model_color_map.get(model_name, default_color)
        annotated_image = draw_boxes(annotated_image, boxes, confidences, classes, class_names, model_name, color, legend)

        # Store confidences data, multiply by 100
        if boxes.size > 0:  # Only store if there are detected objects
            confidences_data[model_name] = [conf * 100 for conf in confidences]

    # Draw legend
    draw = ImageDraw.Draw(annotated_image)
    font = ImageFont.truetype("test.ttf", 15)
    legend_x, legend_y = 10, 10
    for model_name, color in legend:
        draw.rectangle([legend_x, legend_y, legend_x + 20, legend_y + 20], fill=color)
        draw.text((legend_x + 30, legend_y), model_name, fill="black", font=font)
        legend_y += 30

    # Convert the annotated image to Base64
    img_byte_arr = BytesIO()
    annotated_image.save(img_byte_arr, format='PNG')
    img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    return jsonify({
        'image': img_base64,
        'confidences': confidences_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)