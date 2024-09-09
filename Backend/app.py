import os
import mediapipe as mp
from flask import Flask, request, jsonify
from mediapipe.tasks import python
from mediapipe.tasks.python.components import processors
from mediapipe.tasks.python import vision

app = Flask(__name__)

# Initialize the ImageClassifier once
base_options = python.BaseOptions(model_asset_path='classifier.tflite')
options = vision.ImageClassifierOptions(
    base_options=base_options, max_results=4)
classifier = vision.ImageClassifier.create_from_options(options)

# Define the upload folder path
UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/generate-instructions', methods=['POST'])
def generate_instructions():
    if 'screenshots' not in request.files or len(request.files.getlist('screenshots')) == 0:
        return jsonify({'error': 'No files uploaded.'}), 400

    images = []
    predictions = []

    try:
        # Iterate through uploaded files
        for file in request.files.getlist('screenshots'):
            # Save each file temporarily
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Load the input image using MediaPipe
            image = mp.Image.create_from_file(file_path)

            # Classify the input image
            classification_result = classifier.classify(image)

            # Process the classification result (store for later use)
            top_category = classification_result.classifications[0].categories[0]
            predictions.append(f"{top_category.category_name} ({top_category.score:.2f})")

            # Keep the image for visualization or further processing (if needed)
            images.append(image)

            # Clean up the saved image file after classification
            if os.path.exists(file_path):
                os.remove(file_path)

        # Return the classification results
        return jsonify({'predictions': predictions}), 200

    except Exception as e:
        print(f"Error processing images: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the images.'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
