from dynamo_app import scan_faiss_pending, update_content_vec, update_summary_vec
import io
import os
import time
import pprint
import numpy as np  # in faiss layer
import json


EFS_ROOT = "/mnt/efs"
MAX_RECORDS_PER_RUN = 600 # 9 min / 0.87 seconds per record for fais processing (allow 6 minutes for loading and saving)

def lambda_handler(event, context):

    try:
        print("Check for new records in dynamo")
        faiss_pending_entries = scan_faiss_pending()

        if len(faiss_pending_entries) > 0:
            try:
                from faiss_app import FaissApp
            except ImportError:
                print("Faiss loading failed")
        else:
            print("No new records to process")
            return { 'success': True }

        print("Create lists form new records")
        text_lists = {}
        id_lists = {}
        for entry in faiss_pending_entries[:MAX_RECORDS_PER_RUN]:
            content_group = entry["content_group"]
            if content_group not in text_lists:
                text_lists[content_group] = []
                id_lists[content_group] = []
            content_id = str(entry["content_id"])
            text_lists[content_group].append(entry["content"])
            id_lists[content_group].append(content_id)

        for content_group in text_lists:
            print(f"Processing content_group {content_group} with faiss")
            faiss_app = FaissApp(content_group=content_group)

            print("Calculate embeddings and save faiss")
            embeddings, faiss_ids = faiss_app.save_faiss_model(text_lists[content_group], id_lists[content_group])

            print("Save embeddings")
            for embedding, content_id, faiss_id in zip(embeddings, id_lists[content_group], faiss_ids):
                embeddings_json = json.dumps(embeddings.tolist())
                update_content_vec(content_group, content_id, embeddings_json, faiss_id)

            print(f"Finished content_group {content_group}")

    except Exception as e:
        print(e)
        raise e

    return { 'success': True }
 