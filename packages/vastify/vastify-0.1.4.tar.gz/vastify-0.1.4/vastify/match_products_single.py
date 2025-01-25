import json
import uuid
import logging
from collections import defaultdict
from typing import Dict, List, Set, Tuple

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from tqdm import tqdm

from .decorator import run_on_vastai

###############################################################################
# LOGGER SETUP
###############################################################################
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("matcher_debug.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

###############################################################################
# GLOBALS
###############################################################################

# Classification model + tokenizer
CLASSIFIER_MODEL = None
CLASSIFIER_TOKENIZER = None

# Device
DEVICE = None

# Embedding Model
EMBED_MODEL = None

# In-memory vector store: {brand_cat_key: {"embeddings": np.ndarray, "metadata": List[dict]}}
VECTOR_STORE = {}

# For each representative, we track the entire matched group
GROUP_MAP = {}

# Threshold for classification
CLASSIFICATION_THRESHOLD = 0.988

# All representatives, stored for brute-force searching if use_vector_store=False
ALL_REPRESENTATIVES = []

# Boolean indicating whether to build & use the vector store
USE_VECTOR_STORE = True

###############################################################################
# UTILITY FUNCTIONS
###############################################################################


def load_unmatched_representatives(pipeline_path: str) -> Tuple[List[dict], Dict[str, Set[str]]]:
    logger.info(f"Loading unmatched representatives from {pipeline_path}.")
    products = []
    with open(pipeline_path, "r") as f:
        for line in f:
            products.append(json.loads(line))

    logger.info(f"Loaded {len(products)} products from the pipeline.")
    id_to_product = {}
    for p in products:
        if "product_id" not in p:
            raise
        id_to_product[p["product_id"]] = p

    logger.info(f"Loaded {len(id_to_product)} products with IDs.")
    adjacency = defaultdict(set)
    for p in products:
        pid = p["product_id"]
        if "matches" in p and p["matches"]:
            for mid in p["matches"]:
                if mid in id_to_product:  # Only add valid IDs
                    adjacency[pid].add(mid)
                    adjacency[mid].add(pid)

    visited = set()
    representatives = []
    group_map = {}

    logger.info(f"Loaded adjacency list with {len(adjacency)} edges.")

    def dfs_collect(start_id):
        stack = [start_id]
        connected = set()
        while stack:
            curr = stack.pop()
            if curr in visited:
                continue
            visited.add(curr)
            connected.add(curr)
            for neigh in adjacency[curr]:
                if neigh not in visited:
                    stack.append(neigh)
        return connected

    for p in products:
        pid = p["product_id"]
        if pid not in visited:
            connected_ids = dfs_collect(pid)
            rep_id = sorted(connected_ids)[0]
            if rep_id not in id_to_product:  # Handle missing IDs
                logger.warning(
                    f"Representative ID {rep_id} is missing from the product list.")
                continue
            rep_product = id_to_product[rep_id]
            representatives.append(rep_product)
            group_map[rep_id] = connected_ids

    logger.info(
        f"Loaded {len(representatives)} unique representatives from {len(products)} products.")
    return representatives, group_map


def get_matching_string(left_product: dict, right_product: dict) -> str:
    lp = left_product.get("parsed_product_data", {})
    rp = right_product.get("parsed_product_data", {})
    left_str = f"[BRAND] {lp.get('brand','')} [TITLE] {lp.get('title','')} [DESC] {lp.get('description','')}"
    right_str = f"[BRAND] {rp.get('brand','')} [TITLE] {rp.get('title','')} [DESC] {rp.get('description','')}"
    return " ###### " + left_str + " " + right_str


def get_category_batch_probs(
    texts: List[str],
    model: AutoModelForSequenceClassification,
    tokenizer: AutoTokenizer,
    device: torch.device,
    threshold: float
) -> List[bool]:
    logger.debug(f"Classifying a batch of size {len(texts)}.")
    inputs = tokenizer(
        texts, return_tensors="pt", padding=True, truncation=True, max_length=512
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    probabilities = F.softmax(logits, dim=-1)
    match_probs = probabilities[:, 1]
    return (match_probs > threshold).tolist()

###############################################################################
# VECTOR STORE FUNCTIONS
###############################################################################


def build_vector_store(representatives: List[dict], embed_model, brand_cat_filter: bool = True):
    """
    Builds an in-memory vector store. Stores embeddings and metadata by brand-category.
    """
    logger.info(
        f"Building in-memory vector store. Brand-category filtering: {brand_cat_filter}.")
    vector_store = defaultdict(lambda: {"embeddings": [], "metadata": []})

    for rep in tqdm(representatives, desc="Building vector store"):
        brand = rep.get("parsed_product_data", {}).get("brand", "")
        category = rep.get("category", "")
        bc_key = (brand.lower(), category.lower()
                  ) if brand_cat_filter else "all"

        text = f"{rep.get('title','')} {rep.get('description','')[:200]}"
        embedding = embed_model.embed_query(text)

        vector_store[bc_key]["embeddings"].append(embedding)
        vector_store[bc_key]["metadata"].append(
            {"rep_id": rep["product_id"], "product": rep})

    for key in vector_store:
        vector_store[key]["embeddings"] = np.array(
            vector_store[key]["embeddings"])

    logger.info(
        f"In-memory vector store built with {len(vector_store)} brand-category partitions.")
    return vector_store


def similarity_search(query_embedding: np.ndarray, embeddings: np.ndarray, top_k: int = 5):
    """
    Perform cosine similarity search for the query embedding against the stored embeddings.
    """
    similarities = np.dot(embeddings, query_embedding) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
    )
    top_k_indices = np.argsort(similarities)[-top_k:][::-1]
    return top_k_indices, similarities[top_k_indices]

###############################################################################
# INITIALIZATION FUNCTION
###############################################################################


def initialize_matcher(
    pipeline_postproc_path: str,
    classifier_model_path: str,
    tokenizer_model: str,
    embed_model_name: str = "hkunlp/instructor-xl",
    brand_cat_filter: bool = True,
    threshold: float = 0.988,
    use_vector_store: bool = True
):
    logger.info("Initializing matcher with models and vector store.")
    global CLASSIFIER_MODEL, CLASSIFIER_TOKENIZER, DEVICE, EMBED_MODEL
    global VECTOR_STORE, GROUP_MAP, CLASSIFICATION_THRESHOLD
    global ALL_REPRESENTATIVES, USE_VECTOR_STORE

    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    CLASSIFIER_MODEL = AutoModelForSequenceClassification.from_pretrained(
        classifier_model_path).to(DEVICE)
    CLASSIFIER_MODEL.eval()
    CLASSIFIER_TOKENIZER = AutoTokenizer.from_pretrained(tokenizer_model)

    model_kwargs = {"device": DEVICE}
    encode_kwargs = {"normalize_embeddings": True}
    EMBED_MODEL = HuggingFaceInstructEmbeddings(
        model_name=embed_model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    CLASSIFICATION_THRESHOLD = threshold
    USE_VECTOR_STORE = use_vector_store

    # Load unmatched reps and group map
    representatives, group_map = load_unmatched_representatives(
        pipeline_postproc_path)
    GROUP_MAP.clear()
    GROUP_MAP.update(group_map)

    # Store them in ALL_REPRESENTATIVES for possible brute-force searching
    ALL_REPRESENTATIVES.clear()
    ALL_REPRESENTATIVES.extend(representatives)

    # If user wants the vector store, build it
    VECTOR_STORE.clear()
    if USE_VECTOR_STORE:
        VECTOR_STORE.update(build_vector_store(
            representatives, EMBED_MODEL, brand_cat_filter))
    else:
        logger.info("Skipping vector store build (use_vector_store=False).")

    logger.info("Matcher initialization completed.")

###############################################################################
# SINGLE-ITEM PROCESSING
###############################################################################


@run_on_vastai(output_dir="pruned_codebase",
               gpu_name="RTX_2080_Ti",
               price=0.25,
               disk=100.0,
               image='python:3.10-slim',
               num_gpus='1',
               regions=['North_America', 'Europe', 'World'],
               env='-p 70000:8000', include_files=[
                #    'run_on_vastai/bert-product-matcher-weights-v2', 
                   'run_on_vastai/pipeline_postproc.jl'],
               additional_reqs=['sentence-transformers==2.2.2',
                                 'torch==2.2.2',
                                 'instructorembedding==1.0.1',
                                 'huggingface-hub==0.24.1',
                                 'langchain-community==0.3.14'
                                 ])
def process_single_item(new_item: dict, brand_cat_filter: bool = True, max_k: int = 100):
    """
    Now also checks if the global variables are initialized. If not,
    automatically calls initialize_matcher with default paths/params.
    """

    # -------------------------------------------------------------------------
    # >>> ADDED LINES: Auto-initialize if needed <<<
    # -------------------------------------------------------------------------
    global CLASSIFIER_MODEL, CLASSIFIER_TOKENIZER, DEVICE, EMBED_MODEL, VECTOR_STORE, GROUP_MAP
    if (
        CLASSIFIER_MODEL is None or
        CLASSIFIER_TOKENIZER is None or
        DEVICE is None or
        EMBED_MODEL is None or
        not GROUP_MAP  # or some other minimal check
    ):
        logger.info(
            "No prior initialization detected. Initializing with defaults.")
        pipeline_postproc_path = "pruned_codebase/pipeline_postproc.jl"
        classifier_model_path = "pruned_codebase/bert-product-matcher-weights-v2"
        tokenizer_model = "bert-base-cased"
        embed_model_name = "hkunlp/instructor-xl"
        threshold = 0.988
        default_use_vector_store = False

        initialize_matcher(
            pipeline_postproc_path=pipeline_postproc_path,
            classifier_model_path=classifier_model_path,
            tokenizer_model=tokenizer_model,
            embed_model_name=embed_model_name,
            brand_cat_filter=brand_cat_filter,
            threshold=threshold,
            use_vector_store=default_use_vector_store
        )
    # -------------------------------------------------------------------------

    logger.info(
        f"Processing single item: {new_item.get('title', 'Unknown Title')}.")
    global ALL_REPRESENTATIVES, USE_VECTOR_STORE

    if "product_id" not in new_item:
        raise
    if "matches" not in new_item:
        new_item["matches"] = []

    brand = new_item.get("parsed_product_data", {}).get("brand", "")
    category = new_item.get("category", "")
    bc_key = (brand.lower(), category.lower()) if brand_cat_filter else "all"

    # Case 1: If we are using the vector store
    if USE_VECTOR_STORE:
        if bc_key not in VECTOR_STORE:
            logger.info(
                "No vector store found for this brand-category key. Creating new group.")
            GROUP_MAP[new_item["product_id"]] = {new_item["product_id"]}
            return new_item

        query_text = f"{new_item.get('title','')} {new_item.get('description','')[:200]}"
        query_embedding = EMBED_MODEL.embed_query(query_text)
        embeddings = VECTOR_STORE[bc_key]["embeddings"]
        metadata = VECTOR_STORE[bc_key]["metadata"]

        top_k_indices, _ = similarity_search(
            query_embedding, embeddings, top_k=max_k)

        for idx in top_k_indices:
            rep_product = metadata[idx]["product"]
            match_str = get_matching_string(new_item, rep_product)

            if get_category_batch_probs(
                [match_str],
                CLASSIFIER_MODEL,
                CLASSIFIER_TOKENIZER,
                DEVICE,
                CLASSIFICATION_THRESHOLD
            )[0]:
                rep_id = metadata[idx]["rep_id"]
                GROUP_MAP[rep_id].add(new_item["product_id"])
                new_item["matches"] = list(
                    GROUP_MAP[rep_id] - {new_item["product_id"]})
                logger.info(f"Matched with group: {rep_id}.")
                return new_item

        # No match found
        GROUP_MAP[new_item["product_id"]] = {new_item["product_id"]}
        logger.info("No vector-based match found. Created a new group.")
        return new_item

    # Case 2: If we are NOT using the vector store => brute force classification
    else:
        if brand_cat_filter:
            candidates = [
                rep for rep in ALL_REPRESENTATIVES
                if rep.get("parsed_product_data", {}).get("brand", "").lower() == brand.lower()
                and rep.get("category", "").lower() == category.lower()
            ]
        else:
            candidates = ALL_REPRESENTATIVES

        logger.info(
            f"Brute-force checking against {len(candidates)} candidate reps.")

        BATCH_SIZE = 128
        match_strings = []
        candidate_products = []

        for rep in tqdm(candidates, leave=False, desc="Brute-force classification"):
            match_strings.append(get_matching_string(new_item, rep))
            candidate_products.append(rep)

            if len(match_strings) == BATCH_SIZE:
                results = get_category_batch_probs(
                    match_strings,
                    CLASSIFIER_MODEL,
                    CLASSIFIER_TOKENIZER,
                    DEVICE,
                    CLASSIFICATION_THRESHOLD
                )
                for i, is_match in enumerate(results):
                    if is_match:
                        rep_id = candidate_products[i]["product_id"]
                        GROUP_MAP[rep_id].add(new_item["product_id"])
                        new_item["matches"] = list(
                            GROUP_MAP[rep_id] - {new_item["product_id"]})
                        logger.info(
                            f"Matched with group (brute force): {rep_id}.")
                        return new_item

                match_strings = []
                candidate_products = []

        # Final batch
        if match_strings:
            results = get_category_batch_probs(
                match_strings,
                CLASSIFIER_MODEL,
                CLASSIFIER_TOKENIZER,
                DEVICE,
                CLASSIFICATION_THRESHOLD
            )
            for i, is_match in enumerate(results):
                if is_match:
                    rep_id = candidate_products[i]["product_id"]
                    GROUP_MAP[rep_id].add(new_item["product_id"])
                    new_item["matches"] = list(
                        GROUP_MAP[rep_id] - {new_item["product_id"]})
                    logger.info(f"Matched with group (brute force): {rep_id}.")
                    return new_item

        GROUP_MAP[new_item["product_id"]] = {new_item["product_id"]}
        logger.info("No brute-force match found. Created a new group.")
        return new_item


def main():
    # pipeline_postproc_path = "pipeline_postproc.jl"
    # classifier_model_path = "./bert-product-matcher-weights-v2"
    # tokenizer_model = "bert-base-cased"

    # # Decide here whether to use the vector store or not
    # initialize_matcher(
    #     pipeline_postproc_path=pipeline_postproc_path,
    #     classifier_model_path=classifier_model_path,
    #     tokenizer_model=tokenizer_model,
    #     embed_model_name="hkunlp/instructor-xl",
    #     brand_cat_filter=True,
    #     threshold=0.988,
    #     use_vector_store=False
    # )

    with open('run_on_vastai/pipeline_postproc.jl', 'r') as f:
        for line in f:
            item = json.loads(line)
            break

    # logger.info(f"Processing item: {item.get('title', 'Unknown Title')}.")

    # new_product_list = [item] * 1000

    # for new_item in tqdm(new_product_list):
    updated_item = process_single_item(item, brand_cat_filter=True)
    logger.info(f"Updated item: {updated_item}")

    # Optionally append to pipeline_postproc.jl:
    # with open(pipeline_postproc_path, "a") as f:
    #     f.write(json.dumps(updated_item) + "\n")


if __name__ == "__main__":
    logging.basicConfig(
        format='%(levelname)s:%(name)s:%(lineno)d:%(message)s', level=logging.INFO)
    main()
