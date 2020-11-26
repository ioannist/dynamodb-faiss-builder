# sentence_transformers used to create the dense document vectors.
import numpy as np  # in faiss layer
import faiss  # in layer
from pathlib import Path
import zipfile
import sys
import shutil
import os
from s3_app import S3App

# Used to do vector searches and display the results.
# from vector_engine.utils import vector_search, id2details

MAX_WORD_PIECES = 512 # 512 word pieces correspond roughly to 300-400 words; longer texts will be truncated
FAISS_DIR = "/mnt/efs/ml/indexes/faiss"

s3App = S3App(None)

sentence_transformers_dir = '/mnt/efs/ml/libs/python/sentence_transformers/python'
# append the sentence_transformers_dir to PATH so python can find it
if not os.path.exists(sentence_transformers_dir):
    tempdir = '/mnt/efs/tmp/_sentence_transformers'
    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)
    zip_path = s3App.download_sentence_transformers()
    print("Extracting zip")
    zipfile.ZipFile(zip_path, 'r').extractall(tempdir)
    print("Copying extracted files")
    Path(sentence_transformers_dir).mkdir(parents=True, exist_ok=True)
    os.rename(tempdir, sentence_transformers_dir)
print("Importing sentence_transformers")
sys.path.append(sentence_transformers_dir)
from sentence_transformers import SentenceTransformer # make sure this import is AFTER sys.path (format might move it up)

# download distilbert model if not available in efs
distilbert_dir = "/mnt/efs/ml/models/distilbert_base_nli_stsb_mean_tokens"
if not os.path.exists(distilbert_dir):
    tempdir = '/mnt/efs/tmp/_distilbert'
    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)
    zip_path = s3App.download_distilbert()
    print("Extracting zip")
    zipfile.ZipFile(zip_path, 'r').extractall(tempdir)
    print("Copying extracted files")
    Path(distilbert_dir).mkdir(parents=True, exist_ok=True)
    os.rename(tempdir, distilbert_dir)

# Instantiate the sentence-level DistilBERT
# 'distilbert-base-nli-stsb-mean-tokens'
model = SentenceTransformer(distilbert_dir)
model.max_seq_length = MAX_WORD_PIECES


class FaissApp:

    # downloads faiss from s3 and loads it
def load_faiss_index(self):
    # Load and deserialize the Faiss index.
    index_path = f"{FAISS_DIR}/{self.content_group}/{self.content_group}_faiss_index.bin"
    if os.path.exists(index_path):
        return faiss.read_index(index_path)
    else:
        # if there is no faiss model, make a new one
        return faiss.IndexFlatL2(768) # dimensions of distilbert-base-nli-stsb-mean-tokens

    def __init__(self, content_group):
        self.content_group = content_group
        self.index = self.load_faiss_index()

    # updates local faiss with new embeddings and saves it to EFS
    def save_faiss_model(self, text_list, id_list):
        # Convert abstracts to vectors
        embeddings = model.encode(text_list, show_progress_bar=False)
        # Step 1: Change data type
        embeddings32 = np.array(
            [embedding for embedding in embeddings]).astype("float32")
        # Step 4: Add vectors and their IDs
        index_start_id = self.index.ntotal # inclusive
        self.index.add(embeddings32)
        index_end_id = self.index.ntotal # exclsuive
        # serialize index
        Path(f"{FAISS_DIR}/{self.content_group}").mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, f"{FAISS_DIR}/{self.content_group}/{self.content_group}_faiss_index.bin")

        return (embeddings32, range(index_start_id, index_end_id))

    # return top n {text, id} that are semantically similar to given text
    def query(self, text, top_n):
        vector = model.encode(list(text))
        # D (:obj:`numpy.array` of `float`): Distance between results and query.
        # I (:obj:`numpy.array` of `int`): Paper ID of the results
        dists, ids = index.search(
            np.array(vector).astype("float32"), k=num_results)
        # results = [list(df[df.id == idx][column]) for idx in ids[0]]
        return ids
