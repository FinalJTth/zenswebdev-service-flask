from keras.applications.inception_v3 import InceptionV3
from keras.layers import Input
import warnings
warnings.filterwarnings("ignore")
import tensorflow as tf

inception_model = InceptionV3(weights='imagenet', input_tensor=Input(shape=(224, 224, 3)))
inception_model.save('./src/ml/model_h5/inception.h5')

# The export path contains the name and the version of the model
tf.keras.backend.set_learning_phase(0)  # Ignore dropout at inference
model = tf.keras.models.load_model('./src/ml/model_h5/inception.h5')
export_path = './src/ml/model/my_image_classifier/1'
tf.saved_model.save(model, export_path)
# Fetch the Keras session and save the model
# The signature definition is defined by the input and output tensors
# And stored with the default serving key
#with tf.compat.v1.keras.backend.get_session() as sess:
#    tf.saved_model.simple_save(
#        sess,
#        export_path,
#        inputs={'input_image': model.input},
#        outputs={t.name: t for t in model.outputs})