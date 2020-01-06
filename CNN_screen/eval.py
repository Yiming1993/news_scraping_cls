import tensorflow as tf
import numpy as np
import os
from CNN_screen import data_helper
from tensorflow.contrib import learn
from pymongo import MongoClient
from bson import ObjectId

username = ''
password = ''
dbname = ''
host = ''
port = ''
url = 'mongodb://' + username + ':' + password + '@' + host + ':' + port + '/' + dbname
client = MongoClient(url)
db = client[dbname]
# Parameters
# ==================================================


# Eval Parameters
tf.flags.DEFINE_integer("batch_size_test", 64, "Batch Size (default: 64)")
tf.flags.DEFINE_float("dropout_keep_prob_test", 1.0, "Dropout keep probability (default: 0.5)")

# Misc Parameters
tf.flags.DEFINE_boolean("allow_soft_placement_test", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement_test", False, "Log placement of ops on devices")

# Data Parameters
FLAGS = tf.flags.FLAGS

class eval(object):
    def __init__(self):
        pass
    def eval_train(self, time, text_test, textID):
        print("\nParameters:")
        for attr, value in sorted(FLAGS.flag_values_dict().items()):
            print("{}={}".format(attr.upper(), value))
        print("")

        # CHANGE THIS: Load data. Load your own data here

        x_raw = data_helper.load_data_and_labels_screen(text_test)

        # Map data into vocabulary
        today_dir = './CNN_screen/runs/' + str(time) + '/checkpoints'
        vocab_path = os.path.join(today_dir, "..", "vocab")
        vocab_processor = learn.preprocessing.VocabularyProcessor.restore(vocab_path)
        x_test = np.array(list(vocab_processor.transform(x_raw)))

        print("\nEvaluating...\n")

        # Evaluation
        # ==================================================
        checkpoint_file = tf.train.latest_checkpoint(today_dir)
        graph = tf.Graph()
        with graph.as_default():
            session_conf = tf.ConfigProto(
                allow_soft_placement=FLAGS.allow_soft_placement_test,
                log_device_placement=FLAGS.log_device_placement_test)
            sess = tf.Session(config=session_conf)
            with sess.as_default():
                # Load the saved meta graph and restore variables
                saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
                saver.restore(sess, checkpoint_file)

                # Get the placeholders from the graph by name
                input_x = graph.get_operation_by_name("input_x").outputs[0]
                # input_y = graph.get_operation_by_name("input_y").outputs[0]
                dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

                # Tensors we want to evaluate
                predictions = graph.get_operation_by_name("output/predictions").outputs[0]

                # Generate batches for one epoch
                batches = data_helper.batch_iter(list(x_test), FLAGS.batch_size_test, 1, shuffle=False)
                # Collect the predictions here
                all_predictions = []

                for x_test_batch in batches:
                    batch_predictions = sess.run(predictions, {input_x: x_test_batch, dropout_keep_prob: 1.0})
                    all_predictions = np.concatenate([all_predictions, batch_predictions])

            x_eval_ID = textID

            AI_pred = all_predictions.tolist()
            # print(AI_pred)
            # print(x_eval)
            # print(x_eval_ID)
            iterT = 0
            for i in AI_pred:
                if i == 1.0:
                    # print('collect news %s '% x_eval_ID[iterT] +'\n ID: %s' %x_eval_ID[iterT])
                    db.NEWS.update({"_id": ObjectId(x_eval_ID[iterT])}, {'$set': {"alg1_collect": True}}, True, True)
                    iterT += 1
                else:
                    # print('collect news %s '% x_eval_ID[iterT] +'\n ID: %s' %x_eval_ID[iterT])
                    db.NEWS.update({"_id": ObjectId(x_eval_ID[iterT])}, {'$set': {"alg1_collect": False}}, True, True)
                    iterT += 1
                    pass
