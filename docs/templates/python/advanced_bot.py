import dandy as dy

# Setup vision pipeline
vision = dy.Vision.pipeline([
    "detect_objects",
    "segment_image"
])

# Process image
image = dy.Image.load("scene.jpg")
results = vision.process(image)

# Show results
results.visualize()
